package buildKitty;

import org.opencv.core.Core;
import org.opencv.core.CvType;
// import org.opencv.core.CvType;
import org.opencv.core.Mat;
import org.opencv.imgcodecs.Imgcodecs;
import org.opencv.imgproc.Imgproc;

public class ImageBuilder {
    
	public static void main(String[] args){
		// load the core openCV library
        System.loadLibrary(Core.NATIVE_LIBRARY_NAME);
        
        // Instantiating the Imgcodecs class 
        Imgcodecs imageCodecs = new Imgcodecs();

        // Read image of Kitty.
        String file ="C:/Users/joe/Desktop/Photos/kittyBuild/in.jpeg"; 
        Mat input = imageCodecs.imread(file);
        
        // Read image of Music Note.
        String filenote ="C:/Users/joe/Desktop/Photos/kittyBuild/notein3.jpg";
        Mat input2 = imageCodecs.imread(filenote);
        System.out.println("Image Loaded ..........");
        
        // create variables to put image in
        Mat tmp = new Mat();
        Mat tmp2 = new Mat();
        Mat output = new Mat();
        Mat output2 = new Mat();
        
        // convert images to grayscale
        Imgproc.cvtColor(input, tmp, Imgproc.COLOR_RGB2GRAY);
        Imgproc.cvtColor(input2, input2, Imgproc.COLOR_RGB2GRAY);
        
        // convert image to binary
        Imgproc.threshold(tmp, tmp2, 70, 1000, Imgproc.THRESH_BINARY);
        Imgproc.threshold(input2, input2, 70, 1000, Imgproc.THRESH_BINARY);
        
        // Creating kernel matrix
        Mat kernel = Mat.ones(8,8, CvType.CV_32F);
        
        // create a 25x25 matrix
        for(int i = 0; i<kernel.rows(); i++) {
           for(int j = 0; j<kernel.cols(); j++) {
              double[] m = kernel.get(i, j);

              for(int k = 1; k<m.length; k++) {
                 m[k] = m[k]/(8 * 8);
              }
              kernel.put(i,j, m);
           }
        }
        
        // this will smooth out the image but first we need to get the right thresholds I feel.
        Imgproc.filter2D(tmp2, output, -1, kernel);
        // we are skipping the blend for now whilst we search for perfect image.
        // but we will convert it back to a normal picture.
        Imgproc.cvtColor(tmp2, output2, Imgproc.COLOR_GRAY2RGB);
        Imgproc.cvtColor(input2, input2, Imgproc.COLOR_GRAY2RGB);
        
        // create double for storing pixel location.
        double[] data;
        
        // loop through the columns to turn image only red.
        for(int y=0;y<output2.height();y++)
        {
            for(int x=0;x<output2.width();x++)
            {
            	// so this loops through pretty amazing.
            	// load in the image
            	data = output2.get(y, x);
            	//System.out.println(data[0]);
            	//System.out.print(data[1]);
            	//System.out.print(data[2]);
                // data[0] = 0;
                // data[1] = 0;
                // output2.put(y, x, data);
                
                if (data[2] == 0) {
                	data[0] = 0;
                	data[1] = 0;
                	data[2] = 255;
                	output2.put(y, x, data);
                }
            	// System.out.println("Inner loop");
            }
        }
        // awesome, so at this point we now have a pretty cool redscale image
        // it's time to bluescale a music note.
        // blue scale music note is already in black and white.
        // create double for storing pixel location.
        double[] dataNote;
        
        // loop through the columns to turn image only red.
        for(int i=0;i<input2.height();i++)
        {
            for(int j=0;j<input2.width();j++)
            {
            data = input2.get(i, j);
            if (data[2] < 200) {
            	data[0] = 255;
            	data[1] = 0;
            	data[2] = 0;
            	input2.put(i, j, data);
            }
        }
    }
            	
        
        // now time to blend the two images together.
        // first idea is too alternate them
        // second to completely blend in the note.
        for(int a=0;a<output2.height();a++)
        {
            for(int b=0;b<output2.width();b++)
            {
            	if (b % 2 == 0) {
            		data = output2.get(a,b);
            		input.put(a,b, data);
            	} else {
            		data = input2.get(a,b);
            		input.put(a,b, data);
            	}
            }
        
        }
        // writing the image
        String file2 = "C:/Users/joe/Desktop/Photos/kittyBuild/out.jpg"; 
        imageCodecs.imwrite(file2, output2);
        
        // output the note image to test load is working
        String file2a = "C:/Users/joe/Desktop/Photos/kittyBuild/outNote3.jpg"; 
        imageCodecs.imwrite(file2a, input2);
        
        String file2b = "C:/Users/joe/Desktop/Photos/kittyBuild/final.jpg"; 
        imageCodecs.imwrite(file2b, input);
        System.out.println("Image Saved ............");
        
}
}