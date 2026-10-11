import streamlit as st
from kit_builder import build_kit

st.set_page_config(page_title="Tablescape", page_icon="🍋", layout="wide")

st.markdown("""
<style>
.block-container {padding-top: 2.5rem; max-width: 1100px;}
h1 {font-weight: 600; letter-spacing: -0.5px;}
.hero-sub {color: #6b6b6b; font-size: 1.15rem; margin-top: -0.6rem; margin-bottom: 1.5rem;}
.price {font-size: 1.25rem; font-weight: 600;}
</style>
""", unsafe_allow_html=True)

EXAMPLES = {
    "🍋 Italian garden": "Hand-painted bright yellow lemons and fresh green olive branches with small white blossoms, on a crisp white background, light and airy, medium-scale motifs",
    "💙 Blue & white": "Delicate blue wildflowers and small leaves in a classic block-print style, on a clean white background, fresh and timeless",
    "🌸 Blush romance": "Soft blush pink peonies and eucalyptus leaves with tiny gold accents, on an ivory background, delicate watercolor style, elegant and romantic",
}

if "theme" not in st.session_state:
    st.session_state["theme"] = list(EXAMPLES.values())[0]

st.title("Tablescape")
st.markdown('<p class="hero-sub">Describe your event once. Get a matching, priced dinner kit, made on demand.</p>',
            unsafe_allow_html=True)

st.caption("Try an example:")
cols = st.columns(len(EXAMPLES))
for col, (name, prompt) in zip(cols, EXAMPLES.items()):
    if col.button(name, use_container_width=True):
        st.session_state["theme"] = prompt

st.text_area("Describe your theme", key="theme", height=90)
guests = st.number_input("Number of guests", min_value=8, max_value=300, value=24, step=8)

if st.button("Design my kit", type="primary"):
    try:
        with st.status("Designing your kit (this takes a minute or two)...", expanded=True) as status:
            kit = build_kit(st.session_state["theme"], int(guests), on_progress=st.write)
            status.update(label="Your kit is ready", state="complete", expanded=False)
        st.session_state["kit"] = kit
        st.session_state["kit_guests"] = int(guests)
    except Exception:
        st.error("Something went wrong while designing your kit, probably a busy moment on the API. "
                 "Please wait a few seconds and try again.")

kit = st.session_state.get("kit")
if kit:
    st.divider()
    left, right = st.columns([1, 2], gap="large")

    with left:
        st.image(kit["patternImage"], caption="Your custom pattern", width=320)
        st.caption(f"Planned for {st.session_state['kit_guests']} guests at {kit['tables']} tables")

    with right:
        st.subheader("Your matching dinner kit")
        good = [it for it in kit["items"] if "error" not in it]
        failed = [it for it in kit["items"] if "error" in it]

        card_cols = st.columns(max(len(good), 1))
        for col, it in zip(card_cols, good):
            with col:
                  with st.container(border=True, height=520):
                    st.image(it["imageUrl"])
                    st.markdown(f"**{it['item']['label']}**")
                    st.caption(it["options"])
                    st.markdown(f'<span class="price">${it["lineTotal"]:,.2f}</span>', unsafe_allow_html=True)
                    st.caption(f"{it['quantity']} × ${it['unitPrice']:.2f}")

        for it in failed:
            st.warning(f"{it['item']['label']} couldn't be made this time, so it was left out.")

        st.metric("Estimated total", f"${kit['total']:,.2f}")
        st.caption("Estimate before volume discounts, shipping and tax. Your final price appears at checkout.")
        if kit["checkoutUrl"]:
            st.link_button("Go to checkout", kit["checkoutUrl"], type="primary")

st.divider()
st.caption("Made with the Arcade API: one pattern, matching products, instant pricing, drop-shipped.")