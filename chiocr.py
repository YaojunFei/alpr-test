from PIL import Image
import pytesseract
path = '.\\ocrtest.jpg'
str = pytesseract.image_to_string(Image.open(path), lang="chi_sim+eng")
print str.decode('UTF-8')
