package com.eka.ekaconnect.controllers;

import static io.restassured.RestAssured.given;
import static org.hamcrest.CoreMatchers.anyOf;
import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.CoreMatchers.is;
import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.greaterThan;

import java.io.File;
import java.io.FileInputStream;
import java.io.UnsupportedEncodingException;
import java.net.URL;
import java.util.Base64;
import java.util.HashMap;
import java.util.Map;
import java.util.Properties;

import org.testng.annotations.BeforeTest;
import org.testng.annotations.DataProvider;
import org.testng.annotations.Test;

import io.restassured.RestAssured;
import io.restassured.path.json.JsonPath;
import io.restassured.response.Response;

import org.springframework.util.ResourceUtils;

public class PropertyControllerTest {

	String token = null;
	String tenant = null;
	String userName = null;
	String password = null;
	Map<String, Object> requestPayload = new HashMap<String, Object>();

	private static final String tokenGenerationApiPath = "/api/authenticate";
	private static final String tokenValidationError = "Access token is missing";
	private static final String randomToken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOlsicmVzdF9hcGkiXSwidXNlcl9uYW1lIjoiZWthdXNlckBla2FwbHVzLmNvbSIsInNjb3BlIjpbInRydXN0IiwicmVhZCIsIndyaXRlIl0sImV4cCI6MTU2MjY2NzQyNywiYXV0aG9yaXRpZXMiOlsiMTI3LjAuMC4xIl0sImp0aSI6IjE4NTFiNGQ0LTI0ZGEtNDE0OS1hY2I1LTc4MGY5ZGYzZTk1MSIsImNsaWVudF9pZCI6IjIiLCJ0aWQiOiI0NDMifQ.KeKbX1qy2AYVP0f-gRb8orrtbgZQrXZPGcCDj_DktHQ";
	private static final String randomAppUUID = "467a28cc-bc93-4e38-8ff5-0a56ae128f3b";

	/**
	 * setup the connection details from properties file.Property File maybe
	 * application.properties or some other property file. Read tenant,connect host,
	 * port ,platform userName and password from properties file.Generate the token
	 * using authenticateUser() method
	 * 
	 * @see {@link #authenticateUser(String, String)}
	 */
	@BeforeTest
	public void setUp() throws Exception {

		Properties prop = new Properties();
		prop.load(new FileInputStream(ResourceUtils.getFile("classpath:RestAssuredTest.properties")));
		tenant = prop.getProperty("tenant");
		URL url = new URL((String) prop.getProperty("eka_connect_host"));
		RestAssured.baseURI = "http://" + url.getHost();
		RestAssured.port = url.getPort();
		userName = prop.getProperty("userName");
		password = prop.getProperty("password");
		token = authenticateUser(userName, password);
	}

	/**
	 * Test GET apis when either null token is passed or some random/old incorrect
	 * token is passed . Uses dataProvider feature of testNG to pass test data into
	 * this method,thus making it a data-driven test .
	 * 
	 * @see {@link #createTokenTestDataForGet()} -this method is a data provider
	 *      with @DataProvider annotation. Specific "name" is given to dataProvider
	 *      , and this name is used to link the dataProvider to the test method .
	 * @see {@link #testGetApisWithoutTokenAndRandomToken} - how this test is linked
	 *      to the dataProvider using (dataProvider =
	 *      "tokenTestParamsForGetMethods") . The data provider provides parameters
	 *      to the test method one by one as elements of the array . We can add any
	 *      data into this array later which we want to test . In this test the
	 *      parameters taken from dataProvider are-
	 * @param method
	 *            the http method of the API being tested
	 * @param path
	 *            the uri path of the API being tested
	 * @param token
	 *            the validation token to be passed
	 * 
	 */
	@Test(dataProvider = "tokenTestParamsForGetMethods", enabled = true)
	public void testGetApisWithoutTokenAndRandomToken(String method, String path, String token) { // -ve case

		given().log().all().header("X-TenantID", tenant).header("Content-Type", "application/json")
				.header("Authorization", token).when().request(method, path).then().assertThat().statusCode(401)
				.body("localizedMessage",
						anyOf(containsString(tokenValidationError), containsString("Invalid access token")));
	}

	@DataProvider(name = "tokenTestParamsForGetMethods")
	private String[][] createTokenTestDataForGet() {
		return new String[][] { { "GET", "/property", "" }, { "GET", "/property", randomToken },
				{ "GET", "/property/eka_ctrm_host", "" }, { "GET", "/property/eka_ctrm_host", randomToken },
				{ "GET", "/property/" + randomAppUUID + "/eka_ctrm_host", "" },
				{ "GET", "/property/" + randomAppUUID + "/eka_ctrm_host", randomToken },
				{ "GET", "/property/" + randomAppUUID + "/all", "" },
				{ "GET", "/property/" + randomAppUUID + "/all", randomToken } };
	}

	/**
	 * Tests other apis (POST,PUT,DELETE) which need body to be passed with the
	 * request . without token the http 401 status code is asserted and theexpected
	 * error message from connect is also asserted
	 * 
	 * @param method
	 *            the http method of API being tested
	 * @param path
	 *            the uri path of the API being tested
	 * @param token
	 *            the auth token whihc is null or incorrect in this test
	 *            specifically
	 */
	@Test(dataProvider = "tokenTestParamsForOtherRequests", enabled = true)
	public void testOtherApisWithoutTokenAndRandomToken(String method, String path, String token) { // -ve case
		given().log().all().header("X-TenantID", tenant).header("Content-Type", "application/json")
				.header("Authorization", token).with().body(requestPayload).when().request(method, path).then()
				.assertThat().statusCode(401).body("localizedMessage",
						anyOf(containsString(tokenValidationError), containsString("Invalid access token")));
	}

	@DataProvider(name = "tokenTestParamsForOtherRequests")
	private String[][] createTokenTestDataForOtherRequests() {
		return new String[][] { { "POST", "/property/" + randomAppUUID + "/list", "" },
				{ "POST", "/property/" + randomAppUUID + "/list", randomToken },
				{ "POST", "/property/date_picker_format", "" }, { "POST", "/property/date_picker_format", randomToken },
				{ "POST", "/property/" + randomAppUUID + "/eka_ctrm_host", "" },
				{ "POST", "/property/" + randomAppUUID + "/eka_ctrm_host", randomToken },
				{ "PUT", "/property/date_picker_format", "" }, { "PUT", "/property/date_picker_format", randomToken },
				{ "PUT", "/property/" + randomAppUUID + "/list", "" },
				{ "PUT", "/property/" + randomAppUUID + "/list", randomToken },
				{ "DELETE", "/property/date_picker_format", "" },
				{ "DELETE", "/property/date_picker_format", randomToken },
				{ "DELETE", "/property/" + randomAppUUID + "/list", "" },
				{ "DELETE", "/property/" + randomAppUUID + "/list", randomToken } };
	}

	@Test(enabled = true)
	public void testListProperty() {
		given().log().all().header("Authorization", token).header("X-TenantID", tenant)
				.header("Content-Type", "application/json").when().request("GET", "/property").then().assertThat()
				.statusCode(200).body("size()", greaterThan(0))
				.body("find { it.propertyName == 'date_picker_format' }.propertyValue", is("YYYY-MM-DD"));
	}

	/**
	 * Tests getPropertyByName at tenant level API of property . Data Provider has
	 * been used to pass the propertyName and expected propertyValue as parameters
	 * to test . Thus , this single test can be used to execute multiple scenarios
	 * which are passed as parameters from the dataProvider.
	 * 
	 * @see {@link #createGetPropertyByNameTestData()} - propertyNames and expected
	 *      propertyValues are stored in the array. More test data can be added into
	 *      this array later. Specific name = "propertyParams" has been given to
	 *      this Data Provider
	 * @see {@link #testGetPropertyDataByName(String, String)} - this is the test
	 *      method which is linked to the Data Provider using dataProvider =
	 *      "propertyParams"
	 * @param propertyName
	 *            the property name passed from Data Provider
	 * @param propertyValue
	 *            the property value expected , passed from Data Provider
	 */
	@Test(dataProvider = "propertyParams", enabled = true)
	public void testGetPropertyDataByName(String propertyName, String propertyValue) {

		given().log().all().pathParam("propertyName", propertyName).header("Authorization", token)
				.header("X-TenantID", tenant).header("Content-Type", "application/json").when()
				.request("GET", "/property/{propertyName}").then().assertThat().statusCode(200)
				.body("propertyValue", equalTo(propertyValue));
	}

	@DataProvider(name = "propertyParams")
	private String[][] createGetPropertyByNameTestData() {

		return new String[][] { { "date_picker_format", "YYYY-MM-DD" },
				{ "upload_url", "http://172.16.5.101:3334/file/contract/5ce4d7f15908010001ad9f0d/upload" } };
	}

	/**
	 * Tests the /all API of getting all properties at app/user level . Asserts the
	 * equality of expected property value and the actual property value obtained in
	 * response
	 */
	@Test(enabled = true)
	public void testGetAllProperty() {
		given().log().all().header("Authorization", token).header("X-TenantID", tenant)
				.header("Content-Type", "application/json").when().request("GET", "/property/" + randomAppUUID + "/all")
				.then().assertThat().statusCode(200).body("size()", greaterThan(0))
				.body("find { it.propertyName == 'eka_ctrm_host' }.propertyValue", is("http://192.168.1.169:8001"));
	}

	/**
	 * Tests the list API of property which gets list of all properties in key value
	 * pair with hierarchy . Asserts equality of expected property value and the
	 * obtained property value in response
	 */
	@Test(enabled = true)
	public void testGetAllPropsByAppWithHierarchy() {
		given().log().all().header("Authorization", token).header("X-TenantID", tenant)
				.header("Content-Type", "application/json").with().body(requestPayload).when()
				.request("POST", "/property/" + randomAppUUID + "/list").then().assertThat().statusCode(200)
				.body("size()", greaterThan(0)).body("eka_ctrm_host", is("http://192.168.1.169:8001"));
	}

	/**
	 * Tests the save property at tenant level API. Asserts equality of sent
	 * property value and the property value after property is saved
	 */
	@Test(enabled = true)
	public void testSaveProperty() {
		given().log().all().header("Authorization", token).header("X-TenantID", tenant)
				.header("Content-Type", "application/json").with().body(createBodyForSaveOrUpdate()).when()
				.request("POST", "/property/interestrate").then().assertThat().statusCode(200)
				.body("propertyValue", is(createBodyForSaveOrUpdate().get("propertyValue")));
	}

	/**
	 * Tests the save property at app level API . Asserts equality of sent property
	 * value and the property value after property is saved
	 */
	@Test(enabled = true)
	public void testSavePropertyForApp() {
		given().log().all().header("Authorization", token).header("X-TenantID", tenant)
				.header("Content-Type", "application/json").with().body(createBodyForSaveOrUpdate()).when()
				.request("POST", "/property/" + randomAppUUID + "/interestrate").then().assertThat().statusCode(200)
				.body("propertyValue", is(createBodyForSaveOrUpdate().get("propertyValue")));
	}

	/**
	 * Tests the update property at tenant level API . Asserts equality of property
	 * value sent for updation and the property value after it has been updated
	 */
	@Test(enabled = true)
	public void testUpdateProperty() {
		given().log().all().header("Authorization", token).header("X-TenantID", tenant)
				.header("Content-Type", "application/json").with().body(createBodyForSaveOrUpdate()).when()
				.request("PUT", "/property/interestrate").then().assertThat().statusCode(200)
				.body("[0].propertyValue", is(createBodyForSaveOrUpdate().get("propertyValue")));
	}

	/**
	 * Tests the update property at app level API . Asserts equality of property
	 * value sent for updation and the property value after it has been updated
	 */
	@Test(enabled = true)
	public void testUpdatePropertyForApp() {
		given().log().all().header("Authorization", token).header("X-TenantID", tenant)
				.header("Content-Type", "application/json").with().body(createBodyForSaveOrUpdate()).when()
				.request("PUT", "/property/" + randomAppUUID + "/interestrate").then().assertThat().statusCode(200)
				.body("[0].propertyValue", is(createBodyForSaveOrUpdate().get("propertyValue")));
	}

	/**
	 * Tests the delete property at tenant level API . Asserts that the response has
	 * sys__isDeleted as true
	 */
	@Test(priority = 1, enabled = true)
	public void testDeletePropertyForTenant() {
		given().log().all().header("Authorization", token).header("X-TenantID", tenant)
				.header("Content-Type", "application/json").with().body(requestPayload).when()
				.request("DELETE", "/property/interestrate").then().assertThat().statusCode(200)
				.body("sys__isDeleted", is(true));
	}

	/**
	 * Tests the delete property at app level API . Asserts that the response has
	 * sys__isDeleted as true
	 */
	@Test(priority = 1, enabled = true)
	public void testDeletePropertyForApp() {
		given().log().all().header("Authorization", token).header("X-TenantID", tenant)
				.header("Content-Type", "application/json").with().body(requestPayload).when()
				.request("DELETE", "/property/" + randomAppUUID + "/interestrate").then().assertThat().statusCode(200)
				.body("sys__isDeleted", is(true));
	}

	private Map<String, Object> createBodyForSaveOrUpdate() {
		Map<String, Object> requestBody = new HashMap<String, Object>();
		requestBody.put("propertyValue", "13");
		return requestBody;
	}

	/**
	 * Method to generate token from platform using the /api/authenticate api.
	 * userName and password are taken from properties file . Copy this method as it
	 * is for your rest assured tests
	 * 
	 * @param username
	 *            the userName
	 * @param password
	 *            the password
	 * @return the token as string after extracting from the response using jsonPath
	 * @throws UnsupportedEncodingException
	 *             when error in base-64 encoding of userName:password
	 */
	private String authenticateUser(String username, String password) throws UnsupportedEncodingException {
		Map<String, Object> body = new HashMap<String, Object>();
		body.put("userName", username);
		body.put("password", password);
		String base64encodedUsernamePassword = Base64.getEncoder()
				.encodeToString((username + ":" + password).getBytes("utf-8"));
		Response response = given().header("Content-Type", "application/json")
				.header("Authorization", "Basic " + base64encodedUsernamePassword).header("X-TenantID", tenant)
				.body(body).when().post(tokenGenerationApiPath);
		JsonPath jsonPath = new JsonPath(response.asString());
		return jsonPath.getString("auth2AccessToken.access_token");
	}
}
