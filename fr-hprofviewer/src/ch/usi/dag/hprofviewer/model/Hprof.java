package ch.usi.dag.hprofviewer.model;

import java.util.HashMap;
import java.util.Map;

public class Hprof {

	private final Map<Long, String> _strings = new HashMap<Long, String>();

	private final Map<Long, HprofLoadedClass> _loadedClasses = new HashMap<Long, HprofLoadedClass>();

	public Map<Long, String> strings() {
		return _strings;
	}

	public Map<Long, HprofLoadedClass> loadedClasses() {
		return _loadedClasses;
	}

	public String getString(long stringId) {
		return _strings.get(stringId);
	}

	public HprofLoadedClass getLoadedClass(long loadedClassId) {
		return _loadedClasses.get(loadedClassId);
	}
}
