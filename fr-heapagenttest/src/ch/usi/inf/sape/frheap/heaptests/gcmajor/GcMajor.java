package ch.usi.inf.sape.frheap.heaptests.gcmajor;

import java.util.HashMap;
import java.util.LinkedList;
import java.util.Map;

public class GcMajor {

	private static LinkedList<Integer> bigList() {
		final LinkedList<Integer> ls = new LinkedList<Integer>();

		for (int i = 0; i < 1000; i++) {
			ls.add(i);
		}

		return ls;
	}

	private static LinkedList<LinkedList<Integer>> work() {
		final LinkedList<LinkedList<Integer>> lls = new LinkedList<LinkedList<Integer>>();

		for (int i = 0; i < 1000; i++) {
			lls.add(bigList());
		}

		return lls;
	}

	public static void main(String[] args) {
		Map<Integer, LinkedList<LinkedList<Integer>>> map = new HashMap<Integer, LinkedList<LinkedList<Integer>>>();

		for (int i = 0; i < 20; i++) {
			map.put(i, work());
		}
	}
}
