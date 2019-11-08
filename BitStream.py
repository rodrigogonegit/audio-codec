
class BitStream:
	"""
	"""

	__fileObject = None
	__byteBuffer = 0
	__idx = 0

	def __init__(self):
		self.__fileObject = open('output_file', 'wb')

	def flush(self):
		self.__writeByte()

	def __writeByte(self):
		if self.__idx == 8:
			print('Hit __writeByte')
			self.__fileObject.write(self.__byteBuffer.to_bytes(1, byteorder='big'))
			self.__byteBuffer = 0

		elif self.__idx < 8:
			bitwise_length = 8 - self.__idx
			self.__byteBuffer = self.__byteBuffer << bitwise_length
			self.__fileObject.write(self.__byteBuffer.to_bytes(1, byteorder='big'))

		else:
			print('KERNEL PANIC')

		self.__idx = 0

	def writeBit(self, bit):
		# print("Byte buffer. Before:", self.__byteBuffer)
		self.__idx = self.__idx + 1

		if bit == 0:
			self.__byteBuffer = self.__byteBuffer << 1

		elif bit == 1:
			self.__byteBuffer = self.__byteBuffer << 1
			self.__byteBuffer = self.__byteBuffer | 1

		if self.__idx == 8:
			self.__writeByte()

		# print("Byte buffer. After:", self.__byteBuffer)

	def close(self):
		self.__fileObject.close()

b = BitStream()

b.writeBit(1)
b.writeBit(0)
b.writeBit(0)
b.writeBit(0)
b.writeBit(0)
b.writeBit(0)
b.writeBit(0)
b.writeBit(1)

b.writeBit(1)

b.flush()
b.close()
