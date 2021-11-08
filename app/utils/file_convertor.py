import base64

def convertor(file):
 image = open(file, 'rb')
 image_read = image.read()
 image_64_encode = base64.encodebytes(image_read) #encodestring also works aswell as decodestring
 print('This is the image in base64: ' + str(image_64_encode))
 return image_64_encode