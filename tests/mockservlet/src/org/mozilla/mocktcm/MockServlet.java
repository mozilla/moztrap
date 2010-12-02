package org.mozilla.mocktcm;

import java.io.BufferedReader;
import java.io.IOException;
import java.net.URLDecoder;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import com.google.gson.Gson;

public class MockServlet extends HttpServlet {

    /**
     * 
     */
    private static final long serialVersionUID = 1L;
    Gson gson = new Gson();
    Step[] steps;
    int currentStep = 0;

    public MockServlet() {
        System.out.println("Mock Servlet loaded");
    }

    protected void doGet(HttpServletRequest request,
            HttpServletResponse response) throws ServletException, IOException {
        
        // print out the request, so we can debug this on the server side.
        String reqStr = request.getRequestURI();
        String reqQuery = request.getQueryString();
        if (reqQuery != null) {
            reqStr = reqStr + "?" + reqQuery;
        }

        String requestBody = "Never set in this request";

        try {
            if (request.getRequestURI() != null
                    && request.getRequestURI().indexOf("/mockdata") > -1) {

                System.out.println("\n\n*************");
                System.out.println("*** Scenario:  " + request.getParameter("scenario"));
                System.out.println("*************\n\n");

                System.out.println("Request: " + reqStr);
                requestBody = getPostData(request).trim();
                
//                String[] dataParam = request.getParameterValues("data");
//                if (dataParam!= null && dataParam.length > 0) {
//                    System.out.println("Elements: " + dataParam.length);
//                    requestBody = dataParam[0];
//                }
                
//                System.out.println(requestBody);
//                System.out.println("Intended Size: " + request.getContentLength());
//                System.out.println("Actual Size: " + requestBody.length());
                
                steps = gson.fromJson(requestBody, Step[].class);
                currentStep = 0;
            }
            // Return the next expected value for the current steps
            else if (steps != null && currentStep < steps.length) {
                System.out.println("Request: " + reqStr);
                response.setContentType("text/xml");               
                
                // if the request doesn't match the expected request in this set of steps, then return
                // an error 401 - Bad Request
                if (!reqStr.equals(steps[currentStep].request)) {
                    response.setStatus(401);
                    response.getWriter().println("Expected request of: " + steps[currentStep].request);
                    System.out.println("Wrong request:  Error 401");
                    System.out.println("          exp:  " + steps[currentStep].request);
                    System.out.println("          act:  " + reqStr);
                    System.out.println("Perhaps you need to add this to the mock data, if this request was right:");
                    System.out.println(", \"request\": \"" + reqStr + "\"");
                }
                else {
                    response.setStatus(steps[currentStep].status);
                    /*
                     * The expected response is sent as JSON within a field of JSON.  So 
                     * I had to encode the embedded JSON.  However, when I return it, I want 
                     * to send it as decoded JSON, so it looks normal and is parse-able.
                     * Therefore, I must decode it here.
                     */
                    String responseStr = URLDecoder.decode(steps[currentStep].response, "UTF-8");
//                    System.out.println(responseStr);
                    response.getWriter().println(responseStr);
                    
                    currentStep++;
                    // we need to empty the steps if this was the last one
                    if (currentStep == steps.length) {
                        steps = null;
                    }
                }

            }
            // no steps were set, but we got a request.  make a request string for making mock data
            else if (steps == null) {
                System.out.println("Request: " + reqStr);
                System.out.println("Unexpected Request.  No steps currently set.");
                System.out.println("Perhaps the mock data should look like this:");
                System.out.println("{\"status\":   \"" + 200 + 
                                "\", \"request\":  \"" + reqStr + 
                                "\", \"response\": \"xxxresponse" + 
                                "\", \"comment\":  \"xxxcomment" + 
                                "\"}");
                
                
            }
            // request not handled, just return error
            else {
                System.out.println("Wasn't handled.  Returning NOT IMPLEMENTED");
                response.setContentType("text/xml");
                response.setStatus(HttpServletResponse.SC_NOT_IMPLEMENTED);
            }
        } catch (com.google.gson.JsonParseException ex) {
            System.out.println("Well, that didn't work...JSON parsing problem parsing this:");
//            System.out.println("Size: " + request.getContentLength());
//            System.out.println(requestBody);
//            ex.printStackTrace();
        }

    }

    
    
    /*
     * These are all handled exactly the same as any request in this mock object. 
     */
    
    
    
    public void doPost(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {
        doGet(request, response);
    }
    
    protected void doDelete(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {
        doGet(request, response);
    }

    protected void doPut(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {
        doGet(request, response);
    }

    /*
     * Helper function
     * Just read the string content of the post data into a string
     */
    protected String getPostData(HttpServletRequest request)
            throws ServletException, IOException {
        BufferedReader reader = new BufferedReader(request.getReader());
        StringBuffer strBuf = new StringBuffer();
        char[] c = new char[request.getContentLength()];
        reader.read(c);
        strBuf.append(c);
        String body = strBuf.toString();
        return body;
    }

}

/**
 * This is used as the java representation of the JSON that comes in to
 * represent the responses for each step of the next test Scenario
 * 
 * @author camerondawson
 * 
 */
class Step {
    int status;
    String request;
    String response;
    String comment;
    

    Step() {
    }
}
