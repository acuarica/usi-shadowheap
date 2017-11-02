package ch.usi.inf.sape.frheap.heaptests.empty;

import java.io.ByteArrayInputStream;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.util.List;

public class Empty {

	public static class SomeClass<A, B> {
		private A a;

		public B foo1() {
			System.out.println("SomeClass.foo1");
			return null;/* Implementation here */
		}

		public A foo2() {
			return a;/* Implementation here */
		}

		public A foo3(A a) {
			return a;/* Implementation here */
		}

		public int foo4(List<A> aList) {
			return 0;/* Implementation here */
		}

		public A foo5(List<A> aList) {
			return a;/* Implementation here */
		}
	}

//	@SuppressWarnings("unused")
//	public static void readFirst(boolean arg) throws FileNotFoundException {
//
//		InputStream is;
//		if (arg) {
//			is = new FileInputStream((String) null);
//		} else {
//			is = new ByteArrayInputStream(null);
//		}
//
//	}

	public static void main(String[] args) throws IOException {
		new SomeClass<Integer, Integer>().foo1();
//		InputStream is;
//		if (args.length == 0) {
//			is = new FileInputStream("");
//		} else {
//			is = new ByteArrayInputStream(null);
//		}
	}
}
