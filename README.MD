# CSP Tech Preview APIs

Python client for interacting with CSP's server-side AI technology preview features, for research purposes.

Use a modern version of python 3 and
`pip install Pillow PyCryptodome`

## Available functions

- `remove_tones`: [Remove screentones from an image](https://www.clip-studio.com/site/gd_en/csp/userguide/csp_userguide/500_menu/500_menu_edit_cleartone.htm#XREF_72770)
- `grayscale_tones`: [Smooth over the screentones in grayscale](https://www.clip-studio.com/site/gd_en/csp/userguide/csp_userguide/500_menu/500_menu_edit_cleartone.htm#XREF_67441)
- `pose`: [Convert images of humans in poses to 3D poses. Uses a proprietary binary "Bone Layout" format that hasn't been reverse-engineered](https://www.clip-studio.com/site/gd_en/csp/userguide/csp_userguide/500_menu/500_menu_file_read_posephoto.htm)
- `colorize`: [Colorize images, using an optional color hint image. Only seems to accept up to 1024px width images.](https://www.clip-studio.com/site/gd_en/csp/userguide/csp_userguide/500_menu/500_menu_edit_autocolor.htm)


## Example usage


```python
c = CSPTechAPI()
with open("test.png", "rb") as f:
    dat = c.grayscale_tones(f.read())
    with open("output.png", "wb") as g:
        g.write(dat)
```