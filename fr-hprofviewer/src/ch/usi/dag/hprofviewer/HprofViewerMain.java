package ch.usi.dag.hprofviewer;

import java.io.BufferedInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.InputStream;

import org.apache.log4j.Logger;

import ch.usi.dag.hprofviewer.parser.HprofParser;

public class HprofViewerMain {

	private final static Logger logger = Logger.getLogger(HprofViewerMain.class);

	/**
	 * @param args
	 * @throws Exception
	 */
	public static void main(String[] args) throws Exception {

		logger.trace("Started");

		String path = "jmap-dump.3479.hprof";

		logger.info("Opening file '" + path + "'...");

		File file = new File(path);

		logger.debug("File size: " + file.length());

		int fileLen = (int) file.length();

		byte[] result = new byte[fileLen];

		InputStream input = new BufferedInputStream(new FileInputStream(file));

		int bytesRead = input.read(result, 0, (int) file.length());

		logger.debug(bytesRead);

		input.close();

		logger.info("Parsing file...");

		/* Hprof hprof = */new HprofParser().parse(result);
	}
}
