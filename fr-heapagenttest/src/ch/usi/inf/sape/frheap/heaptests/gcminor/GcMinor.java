package ch.usi.inf.sape.frheap.heaptests.gcminor;

import java.util.LinkedList;

public class GcMinor {

	private static LinkedList<Integer> bigList() {
		final LinkedList<Integer> l = new LinkedList<Integer>();

		for (int i = 0; i < 1024; i++) {
			l.add(i);
		}

		return l;
	}

	public static void main(String[] args) {
		for (int i = 0; i < 1000000; i++) {
			bigList();
		}
	}
}
