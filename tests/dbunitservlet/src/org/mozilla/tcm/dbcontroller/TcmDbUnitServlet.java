package org.mozilla.tcm.dbcontroller;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.apache.log4j.Logger;
import org.dbunit.DatabaseUnitException;
import org.dbunit.database.DatabaseConfig;
import org.dbunit.database.DatabaseConnection;
import org.dbunit.database.IDatabaseConnection;
import org.dbunit.dataset.IDataSet;
import org.dbunit.dataset.xml.FlatXmlDataSet;
import org.dbunit.dataset.xml.FlatXmlDataSetBuilder;
import org.dbunit.ext.mysql.MySqlDataTypeFactory;
import org.dbunit.operation.DatabaseOperation;


public class TcmDbUnitServlet extends HttpServlet {
    public static final String DB_FILENAME = "tcm_automation_dump.xml";
    private static Logger logger = Logger.getLogger(TcmDbUnitServlet.class);
    IDatabaseConnection connection;
    String host_name;
    /**
     * 
     */

    public TcmDbUnitServlet() {
        logger.info("DbUnit Servlet loaded");
    }

    protected void doGet(HttpServletRequest request,
            HttpServletResponse response) throws ServletException, IOException {
        
        // print out the request, so we can debug this on the server side.
        String reqStr = request.getRequestURI();
        String reqQuery = request.getQueryString();
        if (reqQuery != null) {
            reqStr = reqStr + "?" + reqQuery;
        }
        
        // this is the host name for the database that needs resetting
        host_name = request.getParameter("host");
        if (host_name == null) {
            throw new ServletException("No hostname provided: /?host=yourhost");
        }
        
        if (request.getRequestURI() != null
            && request.getRequestURI().indexOf("/savedb") > -1) {
            
            try {
                connection = getConnection();

                // full database export
                IDataSet fullDataSet = connection.createDataSet();
                
                FlatXmlDataSet.write(fullDataSet, new FileOutputStream(DB_FILENAME));
                logger.info("Database saved");
                     
                response.setStatus(HttpServletResponse.SC_OK);
            } 
            catch (Exception ex) {
                logger.error("Database issue", ex);
                response.setStatus(HttpServletResponse.SC_INTERNAL_SERVER_ERROR);
            } 

        }
        else if (request.getRequestURI() != null
                 && request.getRequestURI().indexOf("/restoredb") > -1) {
            try {
                connection = getConnection();

                // initialize your dataset here
                FlatXmlDataSetBuilder builder = new FlatXmlDataSetBuilder();
                builder.setColumnSensing(true);
                IDataSet dataSet = builder.build(new File(DB_FILENAME));

                try {
                    DatabaseOperation.TRUNCATE_TABLE.execute(connection, dataSet);
                    DatabaseOperation.CLEAN_INSERT.execute(connection, dataSet);
                    logger.info("Database refreshed");
                } finally {
                    connection.close();
                    connection = null;
                }
                     
                response.setStatus(HttpServletResponse.SC_OK);
            } 
            catch (Exception ex) {
                logger.error("Database issue", ex);
                response.setStatus(HttpServletResponse.SC_INTERNAL_SERVER_ERROR);
            } 

        }
        // request not handled, just return error
        else {
            System.out.println("Wasn't handled.  Returning NOT IMPLEMENTED");
            response.setStatus(HttpServletResponse.SC_NOT_IMPLEMENTED);
        }
        response.setContentType("text/plain");
        response.getWriter().println("URI was: " + reqStr);

    }

    private IDatabaseConnection getConnection() throws SQLException, DatabaseUnitException {
        if (connection == null) {
            Connection jdbcConnection = DriverManager.getConnection(
                    "jdbc:mysql://" + host_name + "/tcm?sessionVariables=FOREIGN_KEY_CHECKS=0", "root", "");
            connection = new DatabaseConnection(jdbcConnection);
            DatabaseConfig config = connection.getConfig(); 
            org.dbunit.ext.mysql.MySqlDataTypeFactory dtFactory = new MySqlDataTypeFactory();
            
            config.setProperty("http://www.dbunit.org/properties/datatypeFactory", 
                    dtFactory);
        }
        return connection;
    }

    /*
     * These are all handled exactly the same as any request . 
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

}
