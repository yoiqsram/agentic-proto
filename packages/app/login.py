import streamlit as st


@st.dialog("Let's begin our journey together!")
def register():
    with st.form(key='register'):
        st.text_input('Username')
        st.text_input('Full Name')

        _, mid, _ = st.columns(3)
        with mid:
            st.form_submit_button(
                'Sign up',
                type='primary',
                use_container_width=True
            )


with st.form(key='login'):
    st.header('Login to Trade Advisor!')
    st.divider()

    st.text_input('Username')

    _, mid, _ = st.columns(3)
    with mid:
        st.form_submit_button(
            'Sign in',
            type='primary',
            use_container_width=True
        )

_, mid, _ = st.columns(3)
with mid:
    if st.button(
            'Create new account',
            type='tertiary',
            use_container_width=True
            ):
        register()
