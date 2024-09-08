import opinion.*;

import java.util.*;
import java.io.*;
import java.text.*;
import java.lang.*;

public class CopeOpi_trad{


	public static void main(String[] args){
//		if(args.length < 2){
//			System.out.println("Usage: java CopeOpi filename [option]");
//			System.out.println("-n:normal mode");
//			System.out.println("-d:debug mode:print each sentence and its score");
//			System.out.println("Ex: java CopeOpi test.txt -n");
//			return;
//		}	

		String oneLine="",oneLine1="";
		//Read testing file
		
		try{

			BufferedReader br = new BufferedReader(new FileReader(args[0]));
			FileWriter fwcsv= new FileWriter("out.csv",true);
			opinion.OpinionCore_Enhanced_trad opComp = new opinion.OpinionCore_Enhanced_trad();
			opComp.readDic();
			String docStr="";
			String tokens[];
			while((oneLine = br.readLine()) != null){
				tokens = oneLine.split(" +");
				try{
					BufferedReader br1 = new BufferedReader(new InputStreamReader(new FileInputStream(tokens[0]),"UTF-8"));
//					OpinionObj.fileForSentence = tokens[0];
					while((oneLine1 = br1.readLine()) != null){
//						System.out.println(oneLine1);
						docStr += oneLine1+" ";
					}
//					System.out.println(docStr);
					br1.close();
					
					GregorianCalendar gc = new GregorianCalendar();
					long start_t = gc.getTimeInMillis();
//					System.out.println("tokens: "+tokens);
					double opScore=0;

					if(args[1].equals("-d")) opComp.setDebugMode(true);
//						opComp.setDebugMode(true);

					opScore = opComp.getOpinionScore(docStr,tokens[1]);

					fwcsv.write(tokens[1] + "," + opScore);
					if(opScore > 0.01)
						fwcsv.write(",Positive"+"\n");
					else if(opScore < -0.01)
						fwcsv.write(",Negative"+"\n");
					else
						fwcsv.write(",Neutral"+"\n");
//					System.out.println("Total Score:"+opScore);
//					if(opScore > 0.01) System.out.println("Positive");
//					else if(opScore < -0.01) System.out.println("Negative");
//					else System.out.println("Neutral");
//					OpinionObj.judgeBySentence(docStr,tokens[1],0.1,Integer.parseInt(args[3]));
					GregorianCalendar gc1 = new GregorianCalendar();
					long end_t = gc1.getTimeInMillis();
//					System.out.println(end_t - start_t);
					System.out.println("Processing: " + tokens[1]);
					docStr="";
				}catch(Exception ee){}
			}
			System.out.println("Analyzing Finish");
			br.close();
			fwcsv.close();
//			
//			while((oneLine = br.readLine()) != null){
//				strContent += oneLine;
//			}
//		}catch(Exception e){System.out.println(e.toString());}		

		
//		System.out.println(strContent);
		//Read from standard in
		/*
		System.out.println("???");
		try{
			BufferedReader br = new BufferedReader(new InputStreamReader(System.in, "BIG5"));			
			while((oneLine = br.readLine()) != null && !oneLine.equals("END")){ 
				strContent += oneLine;
			}
		}catch(Exception e){System.out.println(e.toString());}	
*/
		//System.out.println(strContent);
		//Load Opinion Component
//		System.out.println("???");
		
			
			
		}catch(Exception e){System.out.println(e.toString());}		
		
	}
	
}
