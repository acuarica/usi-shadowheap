package ch.usi.inf.sape.frheap.heaptests.simple;


public class Simple {

	private static Simple[] doit() {
		Simple[] a = new Simple[1000];

		for (int i = 1; i < a.length; i++) {
			a[i] = new Simple();
		}

		return a;
	}

	public static void main(String[] args) {
		System.out.println("Starting " + Simple.class.getName());

		Simple[] a = doit();

		System.out.println(a);

		System.out.println("End of " + Simple.class.getName());
	}
}
