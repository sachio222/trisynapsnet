# Adapted from github.com/sachio222/aha4 (MIT), model/modules.py at 446d6db.
# The vision network, DG, PR, CA1 and the bipolar CA3 rules are unchanged.
# New here: k-winners-take-all, the local CA3 rules, covariance and
# Willshaw, and settling from a partial cue (E1c).
"""The brain-region parts of the model.

The layout starts from AHA, the Artificial Hippocampal Algorithm of
Kowadlo, Ahmed and Rawlinson (2019, arXiv 1909.10340). AHA has a frozen
vision network and four hippocampal parts, each named for a brain region.
The paper names each part twice, as Function(Biology). I kept the
biological names for the classes and put the paper's functional name in
each docstring:

    EC      ->  VC(EC)      Vision Component, the long-term memory (LTM)
    DG      ->  PS(DG)      Pattern Separation
    CA3     ->  PC(CA3)     Pattern Completion
    ECToCA3 ->  PR(EC-CA3)  Pattern Retrieval
    CA1     ->  PM(CA1)     Pattern Mapping

EC is the entorhinal cortex, the main link between neocortex and
hippocampus. DG is the dentate gyrus. CA3 and CA1 are fields of the
hippocampus proper (CA stands for cornu Ammonis).

This project rebuilds these parts one at a time until each has a
counterpart in the brain. Experiment E1 changes only how CA3 learns. Two
parts of E1's CA3 are stand-ins and say so: the dense weight matrix and
k-winners-take-all.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

# CA3 rules that store -1/+1 patterns and settle with tanh units. Both come
# from AHA and stay as baselines.
BIPOLAR_RULES = ("pinverse", "hebbian")
# CA3 rules where each synapse changes using only the activity of the two
# cells it connects. Both store 0/1 patterns and settle with k-WTA.
LOCAL_RULES = ("covariance", "willshaw")
CA3_RULES = BIPOLAR_RULES + LOCAL_RULES
# Where local-rule settling begins. "kwta" starts from the cue's k most
# active cells, as in E1 and E1b. "cue" starts from the cue as given, so a
# partial pattern with fewer than k active cells, or one with stray cells,
# reaches the recurrent weights unchanged (added for E1c).
CA3_STARTS = ("kwta", "cue")


def get_top_k(x, k=10, mask_type="pass_through", topk_dim=0, scatter_dim=0):
    """Keeps the top k values of x along one dimension and zeroes the rest.

    Returns a tensor the same size as x. Pick the dimension carefully: for a
    batch you almost always want the units of each sample (dim 1), not the
    batch itself (dim 0).

        Example:
            >>> get_top_k(torch.tensor([1., 2., 3.]), k=1)
            tensor([0., 0., 3.])

    Args:
        x: (tensor) input.
        k: (int) how many values to keep.
        mask_type: (string) "pass_through" keeps the values, "binary" gives
            1 for the top k and 0 elsewhere, "hopfield" gives 1 for the top k
            and -1 elsewhere.
        topk_dim: (int) the dimension to rank over.
        scatter_dim: (int) keep this the same as topk_dim.
    """

    vals, idx = torch.topk(x, k, dim=topk_dim)

    if mask_type == "pass_through":
        return torch.zeros_like(x).scatter(scatter_dim, idx, vals)

    # The mask comes from the winning indices, so ties and negative winners
    # still give exactly k.
    mask = torch.zeros_like(x).scatter(scatter_dim, idx, 1.0)

    if mask_type == "binary":
        return mask
    if mask_type == "hopfield":
        return 2.0 * mask - 1.0

    raise ValueError(
        'Valid options: "pass_through", "hopfield" (-1, 1), or "binary" (0, 1)')


def kwta(x, k):
    """k-winners-take-all: 1 for the k largest units in each row, 0 elsewhere.

    Stand-in for feedback inhibition. In CA3, basket cells collect input from
    the pyramidal cells around them and inhibit all of them back, so only the
    most strongly driven cells keep firing. Here I skip the basket cells and
    pick the k winners directly. Experiment E2 replaces this with modeled
    inhibitory cells.

    Args:
        x: (tensor) input to each cell, shape (batch, cells).
        k: (int) how many cells stay on.
    """
    return get_top_k(x, k, "binary", 1, 1)


def gaussian_kernel(size, std):
    """A normalised 2D Gaussian, size x size, used by the interest filter."""
    ax = torch.arange(size, dtype=torch.float32) - (size - 1) / 2
    g = torch.exp(-(ax**2) / (2 * std**2))
    kernel = torch.outer(g, g)
    return kernel / kernel.sum()


def condition_memorise(x):
    """Turns a 0/1 DG pattern into -1/+1 for the bipolar CA3 rules.

    AHA paper, Appendix A.1: X' = 2 sgn(X) - 1. Hopfield nets store bipolar
    patterns best.
    """
    return 2.0 * (x > 0).float() - 1.0


def condition_recall(y, k=10, gain=10.0):
    """Turns a PR(EC-CA3) output into a cue the bipolar CA3 can settle from.

    AHA paper, Appendix A.2. Each sample is scaled to sum to `gain`, mapped
    to the range [-1, 1], then shifted by an offset (theta in the paper) so
    that at least k units are positive. Anything negative acts as
    inhibition, and the cue is mostly background, so without the shift the
    -1s would swamp the few units that should switch on.

    Args:
        y: (tensor) PR outputs in [0, 1], shape (batch, units).
        k: (int) active units in each stored pattern.
        gain: (float) gamma in the paper, 10.
    """
    z = gain * y / y.sum(dim=1, keepdim=True).clamp_min(1e-8)
    cue = 2.0 * z - 1.0

    # Find the kth and (k+1)th largest values. If fewer than k units are
    # positive, slide the whole sample up so zero falls between them.
    top = torch.topk(cue, k + 1, dim=1).values
    kth, next_one = top[:, k - 1:k], top[:, k:k + 1]
    theta = torch.where(kth <= 0, -(kth + next_one) / 2, torch.zeros_like(kth))
    return cue + theta


class InterestFilter(nn.Module):
    """Suppresses the empty background in the vision code.

    AHA paper, Section 2.4.5 and Appendix B.3. Omniglot drawings are mostly
    blank page, and blank page still makes the convolution fire. This filter
    loosely copies the retina's centre-surround cells with a Difference of
    Gaussians (DoG) kernel, finds the strongest edges, and only lets the
    vision code through at those spots. A Gaussian blur then gives some
    tolerance to where exactly a feature sits.
    """

    def __init__(self, dog_size=7, dog_std=0.82, dog_k=1.6, nms_size=5, k=20,
                 smooth_size=15, smooth_std=2.375, resolution=1e-9):
        super(InterestFilter, self).__init__()
        self.nms_size, self.k, self.resolution = nms_size, k, resolution

        dog = gaussian_kernel(dog_size, dog_std) - gaussian_kernel(dog_size, dog_std * dog_k)
        self.register_buffer("dog", dog[None, None])
        # The blur is a Gaussian, which splits into a row pass and a column
        # pass. Same result, and far faster than a 15x15 kernel on the CPU.
        g = torch.exp(-(torch.arange(smooth_size) - (smooth_size - 1) / 2) ** 2 / (2 * smooth_std**2))
        self.register_buffer("smooth", (g / g.sum()).float())

    def mask(self, images):
        """Returns a (batch, 1, H, W) mask with up to 2k interest points."""

        # Peak finding compares pixels for exact equality, which float32
        # can't do reliably across devices. So the mask is always built in
        # float64 on the CPU, rounded to a fine step to clear the last
        # noise. Move first, then cast: from MPS, .to("cpu", torch.float64)
        # in one call came back as all zeros.
        device = images.device
        x = images.detach().cpu().double()
        dog = self.dog.detach().cpu().double()
        response = F.conv2d(x, dog, padding=dog.shape[-1] // 2)
        response = torch.round(response / self.resolution) * self.resolution

        mask = torch.zeros_like(response)
        # DoG+ catches light-to-dark edges and DoG- catches dark-to-light.
        for r in (response, -response):
            # Non-maxima suppression: keep a pixel only if it beats its
            # neighbours, so one stroke edge gives one point, not a smear.
            peaks = F.max_pool2d(r, self.nms_size, 1, self.nms_size // 2)
            r = r * (r == peaks) * (r > 0)

            flat = r.flatten(1)
            top = get_top_k(flat, self.k, "binary", 1, 1) * (flat > 0)
            mask = mask + top.view_as(r)

        return mask.clamp(max=1.0).float().to(device)

    def forward(self, images, features):
        features = features * self.mask(images)
        b, c, h, w = features.shape
        x = features.reshape(b * c, 1, h, w)
        pad = self.smooth.numel() // 2
        x = F.conv2d(x, self.smooth.view(1, 1, -1, 1), padding=(pad, 0))
        x = F.conv2d(x, self.smooth.view(1, 1, 1, -1), padding=(0, pad))
        return x.reshape(b, c, h, w)


class EC(nn.Module):
    """VC(EC), the Vision Component. Frozen in E1.

    AHA paper, Section 2.4.5 and Table 3. A single-layer sparse convolutional
    network with 121 filters of 10x10, pretrained in aha4 on the Omniglot
    background set. At inference it runs at stride 1 with 4 winners per
    position, then the interest filter, then 4x4 max-pooling, then gets
    flattened: 121 x 13 x 13 = 20449 numbers per drawing. That vector is the
    input to every hippocampal part.

    An even filter width can't be padded evenly, so I pad 4 on the top and
    left and 5 on the bottom and right to keep the map at 52x52.
    """

    def __init__(self, D_in=1, D_out=121, KERNEL_SIZE=10, STRIDE=1, pool=4,
                 interest_filter=True):
        super(EC, self).__init__()
        self.encoder = nn.Conv2d(D_in, D_out, kernel_size=KERNEL_SIZE, stride=STRIDE)
        self.pad = ((KERNEL_SIZE - 1) // 2, KERNEL_SIZE - 1 - (KERNEL_SIZE - 1) // 2)
        self.pool = pool
        self.interest = InterestFilter() if interest_filter else None

    def load_pretrained(self, state_dict):
        """Copies the filters from an aha4 pretraining state dict."""
        self.encoder.load_state_dict({"weight": state_dict["encoder.weight"],
                                      "bias": state_dict["encoder.bias"]})

    def feature_map(self, x, k=4):
        """Sparse filter responses before pooling, (batch, 121, 52, 52)."""
        before, after = self.pad
        z = self.encoder(F.pad(x, (before, after, before, after)))
        z = get_top_k(z, k, topk_dim=1, scatter_dim=1)
        if self.interest is not None:
            z = self.interest(x, z)
        return z

    def forward(self, x, k=4):
        z = F.max_pool2d(self.feature_map(x, k), self.pool, self.pool)
        return z.flatten(1)

    def output_dim(self, image_size=52):
        """How many numbers forward() returns per image."""
        stride = self.encoder.stride[0]
        side = (image_size - 1) // stride + 1
        return self.encoder.out_channels * (side // self.pool) ** 2


class InhibitionMask():
    """Temporarily silences DG neurons that just fired.

    AHA paper, Section 2.4.1. Real neurons have a refractory period after
    they fire. Here a neuron that fires gets fully inhibited, and the
    inhibition decays by gamma each time a new drawing comes in. Calling the
    mask gives 1 where a neuron may pass and close to 0 where it was just
    used, so drawings shown one after another end up on different neurons.
    """

    def __init__(self, dim, gamma=0.95):
        self.dim, self.gamma = dim, gamma
        self.reset()

    def update(self, top_k_sample):
        """Marks the neurons in top_k_sample (0s and 1s) as just fired."""
        if not torch.all((top_k_sample == 0) | (top_k_sample == 1)):
            raise ValueError('Input must be binary (0., 1.) for inhibition mask')

        fired = top_k_sample.reshape(1, self.dim).to(self.inhibition.device)
        self.inhibition = self.gamma * torch.maximum(self.inhibition, fired)

    def reset(self):
        self.inhibition = torch.zeros(1, self.dim)

    def to(self, device):
        self.inhibition = self.inhibition.to(device)
        return self

    def __call__(self):
        return 1.0 - self.inhibition


class DG(nn.Module):
    """PS(DG), Pattern Separation. The dentate gyrus.

    AHA paper, Section 2.4.1. Its job is to work like a hash function:
    similar drawings should come out as very different, non-overlapping
    patterns. It is a single fully connected layer with random weights that
    never trains. Three things push the outputs apart:
      * only the top k of its neurons fire for each drawing (10 of 225 in
        the paper),
      * 25% of the incoming weights are knocked out to zero,
      * neurons that just fired are inhibited for the next drawings.

    The output is a 0/1 pattern with exactly k ones. CA3 stores it, and
    PR(EC-CA3) learns to produce it.
    """

    def __init__(self, D_in, D_out=225, k=10, gamma=0.95, knockout=0.25):
        super(DG, self).__init__()
        self.k = k
        self.fc1 = nn.Linear(D_in, D_out, bias=False)
        nn.init.xavier_uniform_(self.fc1.weight)
        with torch.no_grad():
            keep = (torch.rand_like(self.fc1.weight) >= knockout).float()
            self.fc1.weight.mul_(keep)
        self.fc1.weight.requires_grad_(False)

        self.phi = InhibitionMask(D_out, gamma)

    def reset(self):
        self.phi.reset()

    def forward(self, X):
        Z = self.fc1(X)
        self.phi.to(Z.device)

        # Drawings go through one at a time, because each one's winners
        # inhibit the next one's.
        out = torch.zeros_like(Z)
        for i in range(Z.shape[0]):
            s = get_top_k(Z[i:i + 1] * self.phi(), self.k, "binary", 1, 1)
            self.phi.update(s)
            out[i] = s[0]

        return out


class ECToCA3(nn.Module):
    """PR(EC-CA3), Pattern Retrieval. The path from EC straight into CA3.

    AHA paper, Section 2.4.3. DG makes a new pattern for every drawing, even
    a second copy of the same character, so DG can't help you find an old
    memory. This network learns to map the vision code of a drawing to the
    DG pattern that was stored for it. Because vision codes of similar
    drawings overlap, a new drawing of a studied character tends to
    retrieve the right memory.

    Two layers, 1000 hidden units, leaky ReLU then sigmoid, trained as
    multi-label classification with binary cross-entropy. It learns by
    backpropagation, which a later experiment replaces.
    """

    def __init__(self, D_in, D_out=225, hidden=1000):
        super(ECToCA3, self).__init__()
        self.fc1 = nn.Linear(D_in, hidden)
        self.fc2 = nn.Linear(hidden, D_out)

    def logits(self, x):
        """Pre-sigmoid outputs, for a numerically stable loss."""
        return self.fc2(F.leaky_relu(self.fc1(x)))

    def forward(self, x):
        return torch.sigmoid(self.logits(x))


class CA3():
    """PC(CA3), Pattern Completion. A recurrent autoassociative memory.

    AHA paper, Section 2.4.2. CA3 pyramidal cells connect back to each
    other, so CA3 can work as a content-addressable memory: store some
    patterns, hand it a noisy or partial one, and it settles on the closest
    stored pattern. It stores in one shot.

    The weight matrix is dense, with any sign: every cell connects to every
    other cell. That is a stand-in. Real CA3 cells contact a few percent of
    their neighbours, and excitatory cells make only positive synapses.
    Experiment E2 adds that wiring.

    Two families of rules:

    Bipolar rules, from AHA ("pinverse", "hebbian"). Patterns are -1/+1,
    cells are graded tanh units with gain 2.7, and each of 70 steps updates
    20 randomly chosen cells (paper Table 3).

    Local rules ("covariance", "willshaw"). Patterns are DG's 0/1 output,
    cells are on or off, and recall keeps the k most driven cells at each
    step (see kwta). The cue is the PR(EC-CA3) output, and it can keep
    driving CA3 during recall with strength cue_weight, the way EC input to
    CA3 may persist while the network settles. With start="kwta" (the
    default) settling begins from the cue's k most active cells. With
    start="cue" it begins from the cue as given, so the first update is
    kWTA(cue W + cue_weight cue). Bipolar rules always begin from the cue
    itself and ignore start.
    """

    def __init__(self, dim1, gain=2.7, n_update=20, n_iter=70, k=10, cue_weight=0.0,
                 start="kwta"):
        if start not in CA3_STARTS:
            raise ValueError("start must be one of {}".format(", ".join(CA3_STARTS)))
        self._train_method = {
            "hebbian": self._hebbian,
            "pinverse": self._pinverse,
            "covariance": self._covariance,
            "willshaw": self._willshaw,
        }
        self.dim1 = dim1
        self.gain, self.n_update, self.n_iter = gain, n_update, n_iter
        self.k, self.cue_weight, self.start = k, cue_weight, start
        self.rule = None
        self.W = torch.zeros(dim1, dim1)

    def train(self, X, method="pinverse"):
        """Stores the patterns in X, shape (patterns, neurons).

        Bipolar rules take -1/+1 patterns. Local rules take 0/1 patterns.
        """
        if method not in self._train_method:
            raise ValueError("Valid methods are {}".format(", ".join(CA3_RULES)))
        if method in LOCAL_RULES and not torch.all((X == 0) | (X == 1)):
            raise ValueError("Local rules store 0/1 patterns, not -1/+1")
        self.rule = method
        return self._train_method[method](X)

    def update(self, Y, generator=None):
        """Lets each cue in Y settle into an attractor and returns the states."""
        if self.rule in LOCAL_RULES:
            return self._settle_sparse(Y)
        return self._settle_bipolar(Y, generator)

    def settle(self, Y, generator=None):
        """Like update(), and also reports how each cue settled.

        Returns (states, info). info["iterations"] counts, for each cue, the
        steps that changed its state; for the bipolar rules it is the last
        step at which any cell changed sign. info["fixed"] is True where the
        final state is a fixed point: for the local rules, a step left it
        unchanged; for the bipolar rules, one more update of every cell at
        once would flip no sign. The states are exactly update()'s.
        """
        if self.rule in LOCAL_RULES:
            return self._settle_sparse(Y, track=True)
        return self._settle_bipolar(Y, generator, track=True)

    def _settle_bipolar(self, Y, generator=None, track=False):
        """Asynchronous tanh updates, as in AHA.

        Each step picks n_update neurons at random and sets each one from the
        weighted sum of all the others. One neuron at a time is guaranteed to
        converge. 20 at a time is faster and works as well in practice, per
        the paper.
        """
        state = Y.clone()
        n = state.shape[1]
        last = torch.zeros(state.shape[0], dtype=torch.long)
        for t in range(self.n_iter):
            idx = torch.randperm(n, generator=generator)[:self.n_update].to(state.device)
            new = torch.tanh(self.gain * (state @ self.W[:, idx]))
            if track:
                flipped = ((new > 0) != (state[:, idx] > 0)).any(dim=1).cpu()
                last[flipped] = t + 1
            state[:, idx] = new
        if not track:
            return state
        after = torch.tanh(self.gain * (state @ self.W))
        fixed = ((after > 0) == (state > 0)).all(dim=1).cpu()
        return state, {"iterations": last, "fixed": fixed}

    def _settle_sparse(self, cue, track=False):
        """Synchronous k-WTA updates for the local rules.

        The first state is the k most active cells of the cue, or with
        start="cue" the cue itself. Each step, every cell sums its recurrent
        input from the cells now on, plus cue_weight times its cue, and the
        k most driven cells fire next. I stop early once the state stops
        changing, or after n_iter steps.

        Args:
            cue: (tensor) PR(EC-CA3) output in [0, 1], or a 0/1 pattern,
                shape (batch, cells).
        """
        state = cue.clone() if self.start == "cue" else kwta(cue, self.k)
        steps = torch.zeros(cue.shape[0], dtype=torch.long)
        fixed = torch.zeros(cue.shape[0], dtype=torch.bool)
        for _ in range(self.n_iter):
            new = kwta(state @ self.W + self.cue_weight * cue, self.k)
            if track:
                same = (new == state).all(dim=1).cpu()
                fixed |= same
                steps += (~same).long()
            if torch.equal(new, state):
                break
            state = new
        if not track:
            return state
        return state, {"iterations": steps, "fixed": fixed}

    def energy(self, state):
        """Hopfield energy of each state in a batch, -1/2 s W s^T.

        Lower is more stable.
        """
        return -0.5 * ((state @ self.W) * state).sum(dim=1)

    def _hebbian(self, X):
        """Neurons that fire together, wire together, on -1/+1 patterns.

        AHA's Hebbian option. Sparse patterns turned into -1/+1 all share
        most of their -1s, so the weights mostly store that common part and
        recall falls into it. Kept as a baseline.
        """
        W = X.T @ X / X.shape[1]
        W.fill_diagonal_(0)
        self.W = W
        return self.W

    def _pinverse(self, X):
        """Pseudo-inverse (projection) rule, AHA's default.

        W = X^T (X X^T)^-1 X, which equals pinv(X) @ X. Each stored pattern
        maps to itself and is a fixed point. Computing it needs every stored
        pattern at once, so no synapse could run it. Kept as a baseline.
        I compute it in float64 on the CPU because pinverse is not on every
        GPU backend and float32 loses precision here.
        """
        X64 = X.detach().cpu().double()
        self.W = (torch.linalg.pinv(X64) @ X64).float().to(X.device)
        return self.W

    def _covariance(self, X):
        """Covariance rule for sparse patterns (Tsodyks and Feigel'man 1988).

        W = sum over patterns of (x - a)(x - a)^T / N, with coding level
        a = k / N and no self-connections. A synapse between two cells that
        both fire grows, which matches long-term potentiation (LTP). A
        synapse where only one side fires shrinks, which matches
        heterosynaptic long-term depression (LTD). Subtracting a means the
        many cells that stay silent no longer dominate the weights. The
        negative weights break Dale's principle, so E2 moves them into an
        inhibitory population.
        """
        n = X.shape[1]
        a = self.k / n
        D = X - a
        W = D.T @ D / n
        W.fill_diagonal_(0)
        self.W = W
        return self.W

    def _willshaw(self, X):
        """Clipped binary synapses (Willshaw, Buneman and Longuet-Higgins 1969).

        W = clip(sum over patterns of x x^T, 0, 1), with no
        self-connections. Each synapse is off until its two cells fire
        together once, then on for good. All weights are positive, as for an
        excitatory synapse that is either potentiated or not.
        """
        W = (X.T @ X).clamp(max=1.0)
        W.fill_diagonal_(0)
        self.W = W
        return self.W

    def reset(self):
        """Resets weight matrix to 0."""
        self.W = torch.zeros(self.dim1, self.dim1, device=self.W.device)
        self.rule = None


class CA1(nn.Module):
    """PM(CA1), Pattern Mapping. Turns a CA3 memory back into a picture.

    AHA paper, Section 2.4.4. CA3 patterns are effectively random symbols.
    CA1 learns to map each one back to what was seen, so a recalled memory
    can be replayed to the neocortex. Like the paper, I train it to rebuild
    the input image.

    Two layers: 100 hidden units, then one output per pixel (52 x 52 =
    2704), leaky ReLU on both, trained with mean squared error (MSE) by
    backpropagation.
    """

    def __init__(self, D_in=225, D_out=2704, hidden=100, image_size=52):
        super(CA1, self).__init__()
        self.image_size = image_size
        self.fc1 = nn.Linear(D_in, hidden)
        self.fc2 = nn.Linear(hidden, D_out)
        nn.init.xavier_uniform_(self.fc1.weight)

    def forward(self, x):
        x = F.leaky_relu(self.fc1(x))
        x = F.leaky_relu(self.fc2(x))
        return x.view(-1, 1, self.image_size, self.image_size)


class CA1ToEC(CA1):
    """E4's backpropagation baseline: PM's network with EC as the target.

    The same two layers, sizes and activations as CA1 (AHA's PM), trained
    the same way, but its output is the drawing's EC code, the 20,449
    numbers the vision network gives, instead of the drawing's pixels. It
    lets one-shot CA1 (CA1BTSP) and backpropagation compare in EC space.
    """

    def __init__(self, D_in=225, D_out=20449, hidden=100):
        super(CA1ToEC, self).__init__(D_in, D_out, hidden, image_size=None)

    def forward(self, x):
        x = F.leaky_relu(self.fc1(x))
        return F.leaky_relu(self.fc2(x))


def btsp_parameters():
    """Every setting of CA1BTSP that is not fixed by the data, with its source.

    source is "chosen" for a value picked on background-alphabet drawings,
    "taken" for a value from a measurement or the published rule, and
    "structural" for a modelling choice that has no number to tune.
    """
    return [
        {"name": "plateau_share", "source": "chosen",
         "why": "share of CA1 cells that get a plateau for each drawing (f_q in Wu and Maass "
                "2025, measured near 0.005); chosen on background-alphabet drawings"},
        {"name": "ec3_baseline", "source": "chosen",
         "why": "a yes-or-no choice: plateau drive measured against each cell's drive from the "
                "mean background-alphabet EC code (yes) or raw (no); chosen on "
                "background-alphabet drawings"},
        {"name": "connect", "source": "taken",
         "why": "probability that a CA3 cell synapses on a CA1 cell, 0.6 (f_w in Wu and Maass "
                "2025, from about 15,000 inputs of 25,000)"},
        {"name": "gate", "source": "taken",
         "why": "probability 0.5 that an eligible synapse changes (Wu and Maass 2025, Eq. 1: "
                "half the 10 s window gives LTP, half LTD)"},
        {"name": "initial_weight", "source": "taken",
         "why": "every CA3-to-CA1 weight starts at 0 (Wu and Maass 2025, Methods)"},
        {"name": "ca1_units", "source": "taken",
         "why": "CA1 cells per CA3 cell, the human ratio 16M/1.7M or the rat ratio 350k/210k"},
        {"name": "window", "source": "structural",
         "why": "each plateau's seconds-long window covers one drawing and no neighbour"},
        {"name": "ec3_projection", "source": "structural",
         "why": "fixed random positive weights in [0, 1) from EC to every CA1 cell decide which "
                "cells plateau: the m most driven (stand-in for the plateau threshold)"},
        {"name": "recall_readout", "source": "structural",
         "why": "k-winners-take-all keeps the m most driven CA1 cells, ties broken at random "
                "(stand-in for feedback inhibition); m is the plateau count, no new value"},
        {"name": "return_rule", "source": "structural",
         "why": "CA1-to-EC weights grow by CA1 activity times EC activity, from zero, no "
                "ceiling; its rate drops out of every cosine score"},
    ]


PLATEAU_SOURCES = ("ec3", "random")


class CA1BTSP():
    """CA1 that learns each drawing in one presentation by BTSP, for E4.

    Biology. A CA1 pyramidal cell gets CA3 input on its proximal dendrites
    and entorhinal layer III (EC3) input on its distal tuft. Strong EC3
    input sets off a dendritic plateau potential (Grienberger and Magee
    2022). A plateau changes the synapses from every CA3 input active within
    a window of seconds around it, in one trial (Bittner and colleagues
    2017), and the change runs both ways depending on the synapse's present
    weight: weak inputs potentiate and strong inputs depress (Milstein and
    colleagues 2021).

    The rule. Wu and Maass (2025, Eq. 1) reduce this to binary synapses:
    when an input arrives within the window of a plateau, with probability
    0.5 a weight at 0 goes to 1 and a weight at 1 goes to 0; otherwise it
    stays. I apply it independently at each synapse, as in their theory and
    simulations. Weights start at 0, and each CA3 cell connects to each CA1
    cell with probability connect (their f_w = 0.6).

    The plateaus. Each drawing's EC code drives every CA1 cell through a
    fixed random projection with positive weights (the instructive EC3
    signal), and the m most driven cells plateau, m = plateau_share x units.
    Picking the top m stands in for a plateau threshold. With ec3_baseline,
    the mean EC code of past drawings, each cell's drive is taken relative
    to its drive from that mean: a stand-in for feedforward inhibition that
    rises with the EC input a cell usually gets. Without it, the few cells
    whose random weights best match the features common to all drawings
    plateau for most drawings (E4 protocol).

    Recall. CA1 sums its CA3 input through the learned binary weights, and
    k-winners-take-all keeps the m most driven cells (ties broken at
    random), a stand-in for feedback inhibition.

    Return to EC. CA1-to-EC synapses learn in the same presentation, after
    the BTSP step, by a Hebbian rule: each grows by the product of its CA1
    cell's activity and its EC unit's activity (Wu and Maass's second step,
    without their ceiling of 1, because EC codes are graded). The CA1
    activity used is CA1's response to the drawing's CA3 pattern right
    after its BTSP step, the trace that recall should bring back. The
    weights R = sum over drawings of outer(trace, EC code) are kept as the
    traces T and codes E, so that R is never built; reinstate() returns
    activity @ T^T @ E, which is exactly activity @ R.

    Everything runs on the CPU.
    """

    def __init__(self, n_in, ec_dim, units, plateau_share=0.005, connect=0.6, gate=0.5,
                 seed=0, plateau_source="ec3", ec3_baseline=None):
        if plateau_source not in PLATEAU_SOURCES:
            raise ValueError("plateau_source must be one of {}".format(", ".join(PLATEAU_SOURCES)))
        self.plateau_source = plateau_source
        self.ec3_baseline = None if ec3_baseline is None else ec3_baseline.detach().float().cpu().flatten()
        self.n_in, self.ec_dim, self.units = n_in, ec_dim, units
        self.plateau_share, self.connect, self.gate, self.seed = plateau_share, connect, gate, seed
        self.m = max(1, int(round(plateau_share * units)))
        g = torch.Generator().manual_seed(self._derive("connect"))
        self.C = torch.rand(units, n_in, generator=g) < connect
        self.W = torch.zeros(units, n_in)
        self.generator = torch.Generator().manual_seed(self._derive("plasticity"))
        self.T = torch.zeros(0, units)
        self.E = torch.zeros(0, ec_dim)

    def _derive(self, *parts):
        import hashlib
        key = ":".join(str(p) for p in ("ca1btsp", self.seed) + parts).encode()
        return int(hashlib.sha256(key).hexdigest()[:15], 16)

    def drive(self, E, block=256):
        """EC3 drive to every CA1 cell, (drawings, units).

        The projection has weights uniform in [0, 1), fixed by the seed. It
        is made in blocks of CA1 cells and never kept, so a large CA1 costs
        no memory. With ec3_baseline set, each drive is P (e - baseline): every
        cell's drive is measured against what the baseline code would give it.
        """
        E = E.detach().float().cpu()
        if self.ec3_baseline is not None:
            E = E - self.ec3_baseline
        out = torch.empty(E.shape[0], self.units)
        for start in range(0, self.units, block):
            stop = min(start + block, self.units)
            g = torch.Generator().manual_seed(self._derive("ec3", start))
            P = torch.rand(stop - start, self.ec_dim, generator=g)
            out[:, start:stop] = E @ P.T
        return out

    def plateaus_from_drive(self, drive):
        """1 for the m most driven cells of each row, 0 elsewhere."""
        return kwta(drive, self.m)

    def plateaus(self, E):
        """Which cells plateau for each EC code, (drawings, units) 0/1.

        With plateau_source="random", a control, m cells drawn at random
        plateau for each drawing, whatever its EC code, as in Wu and Maass's
        own simulations.
        """
        if self.plateau_source == "random":
            g = torch.Generator().manual_seed(self._derive("random plateaus", E.shape[0]))
            return self.plateaus_from_drive(torch.rand(E.shape[0], self.units, generator=g))
        return self.plateaus_from_drive(self.drive(E))

    def btsp(self, x, plateau):
        """One presentation: Wu and Maass's Eq. 1 for one CA3 pattern.

        Args:
            x: (n_in,) CA3 activity, a cell counts as active above 0.
            plateau: (units,) 1 where the CA1 cell has a plateau.
        """
        eligible = (plateau > 0)[:, None] & (x > 0)[None, :] & self.C
        if self.gate < 1:
            eligible &= torch.rand(self.W.shape, generator=self.generator) < self.gate
        self.W = torch.where(eligible, 1.0 - self.W, self.W)
        return self.W

    def respond(self, X):
        """CA1 activity for CA3 states X, (batch, n_in) -> (batch, units) 0/1."""
        X = (X.detach().cpu() > 0).float()
        h = X @ (self.W * self.C).T
        # h counts whole synapses, so a jitter below 1 only orders ties.
        jitter = 0.5 * torch.rand(h.shape, generator=self.generator)
        return kwta(h + jitter, self.m)

    def store(self, X, E):
        """Learns each (CA3 pattern, EC code) pair in one presentation, in order.

        Args:
            X: (drawings, n_in) CA3 patterns, active above 0.
            E: (drawings, ec_dim) EC codes, the drawings' vision codes.
        """
        X = (X.detach().cpu() > 0).float()
        E = E.detach().float().cpu()
        plateaus = self.plateaus(E)
        traces = torch.zeros(X.shape[0], self.units)
        for t in range(X.shape[0]):
            self.btsp(X[t], plateaus[t])
            traces[t] = self.respond(X[t:t + 1])[0]
        self.T = torch.cat([self.T, traces])
        self.E = torch.cat([self.E, E])
        return traces

    def return_weights(self):
        """The CA1-to-EC weights R, (units, ec_dim). Built only for tests."""
        return self.T.T @ self.E

    def reinstate(self, activity):
        """EC code returned by CA1 activity, activity @ R."""
        return (activity.float().cpu() @ self.T.T) @ self.E

    def __call__(self, X):
        """CA3 states -> CA1 activity -> returned EC codes."""
        return self.reinstate(self.respond(X))
