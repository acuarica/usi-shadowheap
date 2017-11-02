package ch.usi.inf.sape.frheap.heaptests.simplearray;

import java.util.LinkedList;
import java.util.List;

public class SimpleArray {

	private static final int THREAD_COUNT = 10;

	SimpleArray next;

	private static final class AppThread extends Thread {
		private final SimpleArray[] array;

		private AppThread(SimpleArray[] array) {
			this.array = array;
		}

		@Override
		public void run() {
			for (int i = 0; i < array.length; i++) {
				array[i] = new SimpleArray();
				array[i].next = new SimpleArray();
			}
		}
	}

	public static void main(String[] args) throws InterruptedException {
		System.out.println("Starting " + SimpleArray.class.getName());

		List<Thread> threads = new LinkedList<Thread>();

		final SimpleArray[] array = new SimpleArray[1000];

		for (int i = 0; i < array.length; i++) {
			array[i] = new SimpleArray();
			array[i].next = new SimpleArray();
		}

		for (int i = 0; i < THREAD_COUNT; i++) {
			Thread t = new AppThread(array);

			threads.add(t);
		}

		for (Thread t : threads) {
			t.start();
		}

		for (Thread t : threads) {
			t.join();
		}

		System.out.println("End of " + SimpleArray.class.getName());
	}
}
