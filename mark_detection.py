import cv2
import pytesseract

pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"

def extract_marks(warp):

    # crop marks obtained column
    marks_region = warp[:, 700:950]

    # cv2.imshow("Marks Region", marks_region)
    # cv2.waitKey(500)

    gray = cv2.cvtColor(marks_region, cv2.COLOR_BGR2GRAY)

    thresh = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        11,
        2
    )
    # strengthen box outlines
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    thresh = cv2.dilate(thresh, kernel, iterations=1)

    # ===== DETECT HORIZONTAL TABLE LINES =====

    horizontal_kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT,
        (120, 1)
    )

    detect_horizontal = cv2.morphologyEx(
        thresh,
        cv2.MORPH_OPEN,
        horizontal_kernel,
        iterations=2
    )

    # cv2.imshow("Horizontal Lines", detect_horizontal)
    # cv2.waitKey(500)

    contours, _ = cv2.findContours(
        detect_horizontal,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    row_lines = []

    for cnt in contours:

        x, y, w, h = cv2.boundingRect(cnt)

        # relaxed horizontal line detection
        if w > 80:
            row_lines.append(y)

    # sort row positions
    row_lines = sorted(row_lines)

    # remove duplicate / nearby lines
    filtered_rows = []

    for y in row_lines:

        # ignore top page border
        if y < 100:
            continue

        if len(filtered_rows) == 0:
            filtered_rows.append(y)
        else:
            # keep separated rows
            if abs(y - filtered_rows[-1]) > 30:
                filtered_rows.append(y)

    row_lines = filtered_rows

    print("Filtered Rows:", row_lines)

    # fallback if no rows detected
    if len(row_lines) < 2:
        h = marks_region.shape[0]

        row_lines = [120, 350, 600, 850, 1100]

        # keep only rows inside image height
        row_lines = [y for y in row_lines if y < h]

        print("Using fallback rows:", row_lines)

    debug = marks_region.copy()

    detected_marks = []

    # ===== PROCESS EACH ROW =====

    for i in range(len(row_lines)-1):

        y1 = row_lines[i]
        y2 = row_lines[i+1]

        row_height = y2 - y1

        # ignore tiny rows
        if row_height < 40:
            continue

        # skip header row
        if y1 < 100:
            continue

        # row crop
        row = thresh[y1:y2, :]

        # ===== SMALL BOX DETECTION OCR =====

        # slightly wider crop for marks column
        marks_crop = row[:, 0:180]

        # strengthen contours
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))

        cleaned = cv2.morphologyEx(
            marks_crop,
            cv2.MORPH_CLOSE,
            kernel,
            iterations=2
        )

        # merge nearby edges so each digit box becomes one contour
        merge_kernel = cv2.getStructuringElement(
            cv2.MORPH_RECT,
            (7,7)
        )

        cleaned = cv2.morphologyEx(
            cleaned,
            cv2.MORPH_CLOSE,
            merge_kernel,
            iterations=2
        )

        cv2.imshow("Cleaned Marks", cleaned)
        # stronger contour image for debugging
        contour_debug = cv2.cvtColor(cleaned, cv2.COLOR_GRAY2BGR)
        cv2.waitKey(150)

        # detect contours
        box_contours, _ = cv2.findContours(
            cleaned,
            cv2.RETR_TREE,
            cv2.CHAIN_APPROX_SIMPLE
        )

        digit_boxes = []

        for cnt in box_contours:
            # approximate contour shape
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)

            bx, by, bw, bh = cv2.boundingRect(cnt)

            aspect = bw / float(bh)
            area = bw * bh

            # detect larger digit boxes instead of tiny contours
            if (
                25 < bw < 120 and
                25 < bh < 120 and
                0.5 < aspect < 1.6 and
                500 < area < 12000 and
                len(approx) >= 4
            ):
                print("Accepted contour:", bx, by, bw, bh)
                cv2.rectangle(
                    contour_debug,
                    (bx, by),
                    (bx + bw, by + bh),
                    (0,255,0),
                    2
                )
                digit_boxes.append((bx, by, bw, bh))

        # sort contours from left to right
        digit_boxes = sorted(
            digit_boxes,
            key=lambda b: b[0]
        )

        # if one large contour covers both boxes, split more carefully
        if len(digit_boxes) == 1:

            bx, by, bw, bh = digit_boxes[0]

            # leave a small center gap between the two boxes
            split_gap = 6

            left_w = (bw // 2) - split_gap
            right_x = bx + (bw // 2) + split_gap
            right_w = bw - left_w - (split_gap * 2)

            digit_boxes = [
                (bx, by, left_w, bh),
                (right_x, by, right_w, bh)
            ]

        # otherwise keep the two right-most contours
        elif len(digit_boxes) >= 2:
            digit_boxes = digit_boxes[-2:]

        # ensure left-to-right OCR order
        digit_boxes = sorted(
            digit_boxes,
            key=lambda b: b[0]
        )

        print("Using contours:", digit_boxes)

        # draw split contours for debugging
        for (dbx, dby, dbw, dbh) in digit_boxes:
            cv2.rectangle(
                contour_debug,
                (dbx, dby),
                (dbx + dbw, dby + dbh),
                (255,0,0),
                2
            )

        cv2.imshow("Accepted Contours", contour_debug)
        cv2.waitKey(150)

        print("Boxes detected:", len(digit_boxes))

        digits = []

        # OCR both handwritten digit boxes
        for idx, (bx, by, bw, bh) in enumerate(digit_boxes[:2]):

            # smaller padding to avoid box borders dominating OCR
            pad = 1

            print("Scanning contour at x:", bx)

            x1 = max(bx - pad, 0)
            y1_box = max(by - pad, 0)
            x2 = min(bx + bw + pad, marks_crop.shape[1])
            y2_box = min(by + bh + pad, marks_crop.shape[0])

            digit = marks_crop[y1_box:y2_box, x1:x2]
            # remove outer border region
            h_crop, w_crop = digit.shape[:2]

            # smaller crop margins so digit strokes are not removed
            crop_margin_x = int(w_crop * 0.10)
            crop_margin_y = int(h_crop * 0.12)

            digit = digit[
                crop_margin_y:h_crop-crop_margin_y,
                crop_margin_x:w_crop-crop_margin_x
            ]

            digit = cv2.resize(digit, (450,450))

            # blur slightly for smoother OCR
            digit = cv2.GaussianBlur(digit, (3,3), 0)

            # sharpen handwritten strokes
            digit = cv2.addWeighted(digit, 1.8, digit, 0, 0)

            # stronger binary image
            _, digit = cv2.threshold(
                digit,
                0,
                255,
                cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
            )

            # enlarge handwritten strokes
            stroke_kernel = cv2.getStructuringElement(
                cv2.MORPH_RECT,
                (2,2)
            )

            digit = cv2.dilate(
                digit,
                stroke_kernel,
                iterations=1
            )

            cv2.imshow(f"Digit Box {idx+1}", digit)
            cv2.waitKey(150)

            text = pytesseract.image_to_string(
                digit,
                config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789'
            ).strip()

            text = text.replace("O", "0")
            text = ''.join(c for c in text if c.isdigit())

            # keep only one final digit
            if len(text) > 1:
                text = text[-1]

            if text == "":
                text = "0"

            print(f"Digit {idx+1} OCR:", text)
            digits.append(text)

            # draw detected boxes
            cv2.rectangle(
                debug,
                (bx, y1 + by),
                (bx + bw, y1 + by + bh),
                (0,255,0),
                2
            )

        while len(digits) < 2:
            digits.append("0")

        final = digits[0] + digits[1]

        print("Detected Row Mark:", final)

        detected_marks.append(final)

    cv2.imshow("Detected Rows", debug)
    cv2.waitKey(1000)
    cv2.destroyAllWindows()

    print("Detected Marks:", detected_marks)

    return detected_marks