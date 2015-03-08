package com.graphhopper;

import com.graphhopper.routing.util.EncodingManager;
import com.graphhopper.util.InstructionList;
import com.graphhopper.util.PointList;
import com.graphhopper.util.Translation;

import java.io.File;
import java.util.Locale;

/**
 * Created with IntelliJ IDEA.
 * User: shayanmasood
 * Date: 15-03-08
 * Time: 4:22 AM
 * To change this template use File | Settings | File Templates.
 */
public class Runner {
    public static void main (String [] args) {
        Double sourceLat = Double.parseDouble(args[0]);
        Double sourceLong = Double.parseDouble(args[1]);
        Double destLat = Double.parseDouble(args[2]);
        Double destLong = Double.parseDouble(args[3]);


        String osmFile = "lowertown.osm";
        GraphHopper hopper = new GraphHopper().forServer();
        hopper.setInMemory();
        hopper.setOSMFile(osmFile);
    // where to store graphhopper files?
        hopper.setGraphHopperLocation("GraphHopper/out/");
        hopper.setEncodingManager(new EncodingManager("car"));

    // now this can take minutes if it imports or a few seconds for loading
    // of course this is dependent on the area you import
        hopper.importOrLoad();

        // simple configuration of the request object, see the GraphHopperServlet classs for more possibilities.
        GHRequest req = new GHRequest(sourceLat, sourceLong, destLat, destLong).
                setWeighting("fastest").
                setVehicle("car");
        GHResponse rsp = hopper.route(req);

    // first check for errors
        if(rsp.hasErrors()) {
            // handle them!
            // rsp.getErrors()
            return;
        }

    // route was found? e.g. if disconnected areas (like island)
    // no route can ever be foun

        // points, distance in meters and time in millis of the full path
        PointList pointList = rsp.getPoints();
        double distance = rsp.getDistance();
        long millis = rsp.getMillis();

        // get the turn instructions for the path

        for (int i =0; i < pointList.size(); i++) {
            System.out.println (pointList.getLatitude(i) + "," + pointList.getLongitude(i));
        }


    }
}
