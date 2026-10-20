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
