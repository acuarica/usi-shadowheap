package ch.usi.dag.hprofviewer.parser;

import java.nio.ByteBuffer;
import java.util.Arrays;

public class BufferReader {

	public int _position = 0;

	private final byte[] _buffer;

	public byte[] getBuffer() {
		return _buffer;
	}

	public BufferReader(byte[] buffer) {
		_buffer = buffer;
	}

	public boolean eob() {
		return _position >= _buffer.length;
	}

	public String readNtString() {
		int i = _position;
		while (i < _buffer.length && _buffer[i] != 0) {
			i++;
		}

		String result = new String(Arrays.copyOfRange(_buffer, _position, i));

		_position = i + 1;

		return result;
	}

	public String readString(int count) {
		return new String(readBytes(count));
	}

	public byte[] readBytes(int count) {
		byte[] result = Arrays.copyOfRange(_buffer, _position, _position + count);

		_position += count;

		return result;
	}

	public byte readByte() {
		final ByteBuffer bb = ByteBuffer.wrap(_buffer);
		byte value = bb.get(_position);
		_position += 1;

		return value;
	}

	public int readInt() {

		final ByteBuffer bb = ByteBuffer.wrap(_buffer);

		int value = bb.getInt(_position);
		_position += 4;

		return value;
	}
}
