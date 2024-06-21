from m4i_atlas_post_install import index


def test_index():
    assert index.hello() == "Hello m4i-atlas-post-install"
