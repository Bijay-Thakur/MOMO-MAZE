from PIL import Image
import numpy as np

img = Image.open(r"D:\Projects\MOMO MAZE\Refrence image\MOMO_MAZE_ALL_19_SCREEN_INDEX.jpg")
w, h = img.size

# Let's inspect thresholding
arr = np.array(img)
# Cream background is typically R > 240, G > 230, B > 210
# Non-cream pixels:
is_bg = (arr[:, :, 0] > 235) & (arr[:, :, 1] > 225) & (arr[:, :, 2] > 200)

# Check row profile of non-bg pixels
non_bg_row = np.mean(~is_bg, axis=1)

# Let's find rows
in_row = False
row_ranges = []
for y in range(70, h):
    val = non_bg_row[y]
    if val > 0.3 and not in_row:
        in_row = True
        r_start = y
    elif val <= 0.3 and in_row:
        in_row = False
        row_ranges.append((r_start, y))
if in_row:
    row_ranges.append((r_start, h))

print("Detected rows:", len(row_ranges), row_ranges)

# For each row, detect column ranges
for idx, (r_s, r_e) in enumerate(row_ranges):
    row_slice = ~is_bg[r_s:r_e, :]
    col_profile = np.mean(row_slice, axis=0)
    in_col = False
    col_ranges = []
    for x in range(w):
        if col_profile[x] > 0.3 and not in_col:
            in_col = True
            c_start = x
        elif col_profile[x] <= 0.3 and in_col:
            in_col = False
            col_ranges.append((c_start, x))
    if in_col:
        col_ranges.append((c_start, w))
    print(f"Row {idx} cols ({len(col_ranges)}):", col_ranges)
