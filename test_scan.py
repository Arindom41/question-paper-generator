from mark_scanner import scan_paper
from mark_detection import extract_marks
import cv2

print("Starting scanner")

image_path = "/Users/arindompratimborah/6th MINI PROJECT/static/scan_papers/SCAN_new_paper.png"

warp = scan_paper(image_path)

print("Scan complete")

marks = extract_marks(warp)

print("After extraction")

print("Detected Marks:", marks)