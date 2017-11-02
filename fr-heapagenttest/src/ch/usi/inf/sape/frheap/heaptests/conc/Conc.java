package ch.usi.inf.sape.frheap.heaptests.conc;

import java.io.ByteArrayInputStream;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.util.LinkedList;
import java.util.List;
import java.util.concurrent.ConcurrentHashMap;

public class Conc {
//	private static final int THREAD_COUNT = 10;
//
//	public static class Element {
//		public int value;
//	}
//
//	//private static final AtomicInteger key = new AtomicInteger(0);
//	private static final ConcurrentHashMap<Integer, Element> map = new ConcurrentHashMap<Integer, Element>();
//
//	private static class AppThread extends Thread {
//
//		@Override
//		public void run() {
//			System.out.format("thread | name: %s, id: %d\n", getName(), getId());
//
//			for (int i = 0; i < 100; i++) {
//				// int k = key.getAndIncrement();
//				map.put(i, new Element());
//			}
//
//			System.out.format("thread | name: %s, id: %d\n", getName(), getId());
//		}
//	}

	public static int main(String[] args) throws IOException {
		InputStream is;
		if (args.length == 0) {
			is = new FileInputStream("");
		} else {
			is = new ByteArrayInputStream(null);
		}
		
		return is.read();
	}
	
//	public static void main32(String[] args) throws InterruptedException {
//		System.out.println("Starting " + Conc.class.getName());
//
//		for (int i = 0; i < 1000; i++) {
//			map.put(i, new Element());
//		}
//
//		List<Thread> threads = new LinkedList<Thread>();
//
//		for (int i = 0; i < THREAD_COUNT; i++) {
//			Thread t = new AppThread();
//			threads.add(t);
//		}
//
//		for (Thread t : threads) {
//			t.start();
//		}
//
//		for (Thread t : threads) {
//			t.join();
//		}
//
//		System.out.println("End of " + Conc.class.getName());
//	}
}
