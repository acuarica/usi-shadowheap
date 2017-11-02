package ch.usi.dag.hprofviewer.model;

import java.util.LinkedList;
import java.util.List;

public class HprofHeapPrimitiveArray {
	public long arrayObjectId;

	public int stackTraceSerialNumber;

	public int numberOfElements;

	public byte elementType;

	public List<Object> values = new LinkedList<Object>();

}
