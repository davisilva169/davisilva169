# Profile artwork

Transparent SVG artwork follows the profile owner's approved design: orange (#E79600), black (#1D1D1B), gray (#9D9D9C), and white, with a handwritten name, spiral galaxy, and personal signature APOETA.

The APOEMA emblem is exported from original vector files supplied by the profile owner. Original vector paths are preserved. Handwritten lettering is outlined from Architects Daughter Regular, supplied with the brand materials, so no font download is required.

The galaxy, branching shower, and energy-sharing diagrams are illustrations, not plots of measured or simulated research results. Dark and light variants use transparent backgrounds to integrate with GitHub's theme.

Run `python scripts/build_header.py` to rebuild the seeded particle field around the galaxy while preserving the outlined name and original logo. Its density tapers toward the name, and the leading orange particle remains larger than the surrounding particles. The identity line is Statistical Physicist and Astrophysicist.

The scheduled workflow runs scripts/update_stats.py daily. Cards are served directly from this repository without relying on a third-party statistics-image service. Commit counts sum contributions attributed to davisilva169 on default branches of owned public, non-fork repositories. Language percentages describe code size reported by GitHub, not proficiency. Private repositories are excluded.

## Workflow and selected-work showcase

Run `python scripts/build_showcase.py` to rebuild the single-image workflow and the five-project showcase. All artwork is native SVG. The showcase uses self-contained CSS animation, highlights one project every six seconds, and needs no JavaScript or external resources. It displays a static first project when reduced motion is requested. Each repository has a normal text link directly below the animation; links inside an embedded SVG image are not used.

Desktop and mobile compositions are separate assets to keep text legible. The shower artwork uses a connected branching tree; the Duffing illustration uses an RK4 trajectory of x'' + 0.2x' - x + x³ = 0.3 cos(1.2t). These are conceptual illustrations, not figures claiming to reproduce a project's research results.
