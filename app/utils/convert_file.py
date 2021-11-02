# import cv2
#
# # read the image file
# img = cv2.imread('/home/krishnakishore/Pictures/img1.jpeg', 2)
#
# ret, bw_img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
#
# # converting to its binary form
# bw = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
#
# cv2.imshow("Binary", bw_img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

from werkzeug.security import generate_password_hash,check_password_hash
import base64
def file_print():
    file = '/home/krishnakishore/UPLOAD/db2.png'
    image = open(file, 'rb')
    image_read = image.read()
    image_64_encode = base64.encodebytes(image_read)  # encodestring also works aswell as decodestring

    # print('This is the image in base64: ' + str(image_64_encode))
    # encoded_string = generate_password_hash(image_64_encode, method='sha256')

    image_64_decode = base64.decodebytes(image_64_encode)
    image_result = open('d.png', 'wb')  # create a writable image and write the decoding result
    image_result.write(image_64_decode)
    # print(encoded_string)


