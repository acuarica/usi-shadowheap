package ch.usi.inf.sape.frheap.heaptests.inner;

public class Inner {

	Inner outerField;

	String value;

	private class InnerInstance {
		// Inner field;

		InnerInstance() {
			value = "Hola que tal";
			// field = outerField;
		}
	}

	public static void main(String[] args) {
		System.out.println("Starting " + Inner.class.getName());

		Inner inn = new Inner();
		// InnerInstance ins =
		inn.new InnerInstance();

		System.out.println(inn.value);

		System.out.println("End of " + Inner.class.getName());
	}

}
