import streamlit as st
from kit_builder import build_kit

st.set_page_config(page_title="Event Kit Designer", layout="wide")
st.title("Event Kit Designer")
st.caption("Describe your event once. Get a matching, priced dinner kit.")

with st.form("kit_form"):
    theme = st.text_input("Describe your theme", "Italian garden, lemons and olive branches")
    guests = st.number_input("Number of guests", min_value=8, max_value=300, value=80, step=8)
    submitted = st.form_submit_button("Design my kit")

if submitted:
    with st.spinner("Designing your kit... this takes a minute or two"):
        st.session_state["kit"] = build_kit(theme, int(guests))

kit = st.session_state.get("kit")
if kit:
    st.subheader("Your design")
    st.image(kit["patternImage"], width=300)
    st.write(f"Planned for {kit['tables']} tables.")

    cols = st.columns(len(kit["items"]))
    for col, it in zip(cols, kit["items"]):
        with col:
            if "error" in it:
                st.warning(f"{it['item']['label']} couldn't be made: {it['error']}")
                continue
            st.image(it["imageUrl"])
            st.markdown(f"**{it['title']}**")
            st.caption(it["options"])
            st.write(f"{it['quantity']} × ${it['unitPrice']:.2f}")

    st.metric("Estimated total", f"${kit['total']:,.2f}")
    st.caption("Estimate only. Volume discounts, shipping and tax are applied at checkout.")
    if kit["checkoutUrl"]:
        st.link_button("Go to checkout", kit["checkoutUrl"])