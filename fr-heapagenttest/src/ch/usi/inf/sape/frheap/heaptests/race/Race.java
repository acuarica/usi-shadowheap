package ch.usi.inf.sape.frheap.heaptests.race;

import java.util.LinkedList;
import java.util.List;

public class Race {

	private static final int THREAD_COUNT = 10;

	public static class Dummy {
		public Dummy field1;
		public Dummy field2;
	}

	private static class TargetThread extends Thread {
		private Dummy[] _data;
		private int _threadIndex;

		public TargetThread(Dummy[] data, int threadIndex) {
			_data = data;
			_threadIndex = threadIndex;
		}

		@Override
		public void run() {
			System.err.format("thread | index: %d, name: %s, id: %d\n", _threadIndex, getName(), getId());

			for (int i = 0; i < _data.length; i++) {
				_data[i].field1 = new Dummy();
				_data[i].field2 = new Dummy();
				// int k = key.getAndIncrement();
				// map.put(threadIndex, threadIndex);
			}

			System.err.format("thread | index: %d, name: %s, id: %d, data count: %d\n", _threadIndex, getName(),
					getId(), 11);
		}
	}

	public static void main(String[] args) throws InterruptedException {
		System.err.println("Starting " + Race.class.getName());

		List<Thread> threads = new LinkedList<Thread>();

		// final AtomicInteger key = new AtomicInteger(0);
		// final ConcurrentHashMap<Integer, Integer> map = new
		// ConcurrentHashMap<Integer, Integer>();

		final int I = 40;
		final int J = 50;
		Dummy[] data = new Dummy[I * J];
		for (int i = 0; i < I; i++) {
			data[i * J] = new Dummy();
			for (int j = 1; j < J; j++) {
				data[i * J + j] = data[i * J];
			}
		}

		for (int i = 0; i < THREAD_COUNT; i++) {
			Thread t = new TargetThread(data, i);

			threads.add(t);
		}

		for (Thread t : threads) {
			t.start();
		}

		for (Thread t : threads) {
			t.join();
		}

		System.err.println("End of " + Race.class.getName());
	}
}
