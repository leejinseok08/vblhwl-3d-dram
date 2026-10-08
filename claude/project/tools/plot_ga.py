# plot_ga.py <dir with <struct>_cut_*.json> <struct> <out prefix> [paper Fig.2 image] : the mini-array mesh (cuts of tools/grd_cut.py)
# drawn by material, alone and next to the views of Fig.2 of Cho et al. (IRPS 2026). Pictures with a crop of the paper's figure
# (<prefix>_vs_fig2_*.png) are for the results folder only, not for the shared repository; <prefix>_cuts.png has no crop.
# Colours follow Fig.2: p silicon dark blue, N+ silicon (BL pillar, source) red, isolation oxide cyan, spacer material olive,
# word-line metal blue, storage node orange, capacitor ground light blue, capacitor dielectric dark red, gate dielectric magenta.
import sys, os, json
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
MAT = {"Silicon": "#1414d2", "Silicon|n": "#ff1e1e", "SiO2": "#19e0f0", "Si3N4": "#d7dc78", "HfO2": "#c800c8", "Insulator1": "#8c0000"}
def concol(n): return {"bl": "#ff1e1e", "wl": "#1e96f0", "sn_": "#ffa500", "snx": "#e6b450", "gp": "#28b4e6"}.get(n[:3] if n[:3] in ("sn_", "snx") else n[:2], "#888888")
LEG = (("p silicon (body)", "#1414d2"), ("N+ silicon (BL, source)", "#ff1e1e"), ("SiO2", "#19e0f0"), ("spacer Si3N4", "#d7dc78"), ("gate dielectric", "#c800c8"),
       ("capacitor dielectric", "#8c0000"), ("WL metal (contact)", "#1e96f0"), ("storage node (contact)", "#ffa500"), ("neighbour's half node", "#e6b450"), ("capacitor ground (contact)", "#28b4e6"))

def draw(ax, d, swap=False, title=""):
    f = (lambda p: [[q[1], q[0]] for q in p]) if swap else (lambda p: p)
    for mat, ps in d["polys"].items(): ax.add_collection(PolyCollection([f(p) for p in ps], facecolors=MAT.get(mat, "#bbbbbb"), edgecolors=MAT.get(mat, "#bbbbbb"), linewidths=0.15))
    for name, lp in d["loops"]:
        lp = f(lp); ax.fill([q[0] for q in lp], [q[1] for q in lp], color=concol(name), lw=0)
    ax.set_aspect("equal"); ax.autoscale(); ax.set_title(title, fontsize=9); ax.tick_params(labelsize=7)

if __name__ == "__main__":
    dd, st, out = sys.argv[1:4]; img = sys.argv[4] if len(sys.argv) > 4 else None
    C = {k: json.load(open(os.path.join(dd, f"{st}_cut_{k}.json"))) for k in ("xsec", "body", "gate", "fin", "cap", "wl")}
    fig, a = plt.subplots(2, 3, figsize=(19, 10))
    draw(a[0, 0], C["xsec"], title=f"along the channel through a row centre (z = {C['xsec']['at_nm']:.0f} nm): paper's Y-Z section")
    draw(a[0, 1], C["cap"], swap=True, title=f"across the rows through the capacitor pillars (x = {C['cap']['at_nm']:.0f} nm)")
    draw(a[0, 2], C["wl"], swap=True, title=f"across the rows through a word line (x = {C['wl']['at_nm']:.0f} nm)")
    draw(a[1, 0], C["body"], title=f"from above at body level (y = {C['body']['at_nm']:.0f} nm)")
    draw(a[1, 1], C["gate"], title=f"from above at main-gate level (y = {C['gate']['at_nm']:.0f} nm)")
    draw(a[1, 2], C["fin"], title=f"from above at the ground-fin level (y = {C['fin']['at_nm']:.0f} nm)")
    for x in a[0]: x.set_xlabel("x or z [nm]", fontsize=8); x.set_ylabel("y = paper's Z [nm]", fontsize=8)
    for x in a[1]: x.set_xlabel("x = paper's Y [nm]", fontsize=8); x.set_ylabel("z = paper's X [nm]", fontsize=8)
    fig.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=c) for _, c in LEG], labels=[l for l, _ in LEG], loc="lower center", ncol=5, fontsize=8)
    fig.suptitle(f"{st}: mesh as built (structure only), cut by planes", fontsize=11); fig.tight_layout(rect=(0, 0.05, 1, 0.97)); fig.savefig(out + "_cuts.png", dpi=110); print("wrote", out + "_cuts.png")
    if img:
        im = plt.imread(img)
        # crops of the embedded Fig.2 image (2017 x 1173): Y-Z section, top view
        for key, crop, ttl, tag in (("xsec", (100, 715, 790, 1060), "Fig.2 of the paper: cross-sectional view (Y-Z)", "xsec"), ("gate", (1100, 140, 1760, 560), "Fig.2 of the paper: top view (X-Y)", "top")):
            fig, a = plt.subplots(1, 3 if key == "gate" else 2, figsize=(21 if key == "gate" else 18, 6.2))
            a[0].imshow(im[crop[1]:crop[3], crop[0]:crop[2]]); a[0].set_title(ttl, fontsize=10); a[0].axis("off")
            if key == "xsec": draw(a[1], C["xsec"], title=f"this model, mesh as built: z = {C['xsec']['at_nm']:.0f} nm (row centre)")
            else:
                draw(a[1], C["gate"], title=f"this model from above at main-gate level (y = {C['gate']['at_nm']:.0f} nm)")
                draw(a[2], C["fin"], title=f"this model from above at the ground-fin level (y = {C['fin']['at_nm']:.0f} nm)")
            for x in a[1:]: x.set_xlabel("x = paper's Y [nm]", fontsize=9); x.set_ylabel(("y = paper's Z" if key == "xsec" else "z = paper's X") + " [nm]", fontsize=9)
            fig.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=c) for _, c in LEG], labels=[l for l, _ in LEG], loc="lower center", ncol=5, fontsize=8)
            fig.tight_layout(rect=(0, 0.08, 1, 1)); fig.savefig(f"{out}_vs_fig2_{tag}.png", dpi=110); print("wrote", f"{out}_vs_fig2_{tag}.png")
