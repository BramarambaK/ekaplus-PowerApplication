package com.eka.power;

import static io.restassured.RestAssured.given;

import java.io.FileInputStream;
import java.io.UnsupportedEncodingException;
import java.net.URL;
import java.util.Base64;
import java.util.HashMap;
import java.util.Map;
import java.util.Properties;

import org.apache.http.HttpStatus;
import org.json.JSONObject;
import org.json.JSONTokener;
import org.springframework.util.ResourceUtils;
import org.testng.Assert;
import org.testng.annotations.BeforeTest;
import org.testng.annotations.Test;

import io.restassured.RestAssured;
import io.restassured.http.Method;
import io.restassured.path.json.JsonPath;
import io.restassured.response.Response;

public class ConnectAPITest {

	String token = null;
	String tenant = null;
	String userName = null;
	String password = null;
	String eka_connect_host = null;
	Map<String, Object> requestPayload = new HashMap<String, Object>();

	private static final String tokenGenerationApiPath = "/api/authenticate";
	private static final String CONTRACT_OBJECT_API = "/data/d7d05837-88a3-471e-a5f1-1c5fd6cec3e7/73314f69-35dc-43c1-a1db-47d755bafd0d";
	private static final String BLOCK_OBJECT_API = "/data/d7d05837-88a3-471e-a5f1-1c5fd6cec3e7/0de25ff5-9c68-48fe-abd8-f8e8d4a4132b";
	private static final String FORMULA_OBJECT_API = "/data/84d7b167-1d9f-406d-b974-bea406a25f9a/formula";

	@BeforeTest
	public void setUp() throws Exception {

		Properties prop = new Properties();
		prop.load(new FileInputStream(ResourceUtils.getFile("classpath:RestAssuredTest.properties")));
		tenant = prop.getProperty("tenant");
		userName = prop.getProperty("userName");
		password = prop.getProperty("password");
		eka_connect_host = (String) prop.getProperty("eka_connect_host");
		URL url = new URL(eka_connect_host);
		RestAssured.baseURI = "http://" + url.getHost();
		RestAssured.port = url.getPort();
		token = authenticateUser(userName, password);
	}

	@Test(enabled = true)
	public void testContractObjectData() throws Exception {
		Response response = callAPI(Method.GET, CONTRACT_OBJECT_API, null);
		verify200OKResponse(response);
	}

	@Test(enabled = true)
	public void testBlockObjectData() throws Exception {

		FileInputStream fileInputStream = new FileInputStream(ResourceUtils.getFile("classpath:block_filter.json"));
		Map<String, Object> jsonMap = new JSONObject(new JSONTokener(fileInputStream)).toMap();

		Response response = given().log().all().header("Authorization", token).header("X-TenantID", tenant)
				.header("Content-Type", "application/json").with().body(jsonMap).when()
				.request(Method.GET, BLOCK_OBJECT_API);
		verify200OKResponse(response);
	}

	@Test(enabled = true)
	public void testFormulaObjectData() throws Exception {
		FileInputStream fileInputStream = new FileInputStream(
				ResourceUtils.getFile("classpath:formula_id_filter.json"));
		Map<String, Object> jsonMap = new JSONObject(new JSONTokener(fileInputStream)).toMap();

		Response response = given().log().all().header("Authorization", token).header("X-TenantID", tenant)
				.header("Content-Type", "application/json").with().body(jsonMap).when()
				.request(Method.GET, FORMULA_OBJECT_API);
		verify200OKResponse(response);
	}

	private String authenticateUser(String username, String password) throws UnsupportedEncodingException {
		Map<String, Object> body = new HashMap<String, Object>();
		body.put("userName", username);
		body.put("password", password);
		String base64encodedUsernamePassword = Base64.getEncoder()
				.encodeToString((username + ":" + password).getBytes("utf-8"));
		Response response = given().header("Content-Type", "application/json")
				.header("Authorization", "Basic " + base64encodedUsernamePassword).header("X-TenantID", tenant)
				.body(body).when().post(eka_connect_host + tokenGenerationApiPath);
		JsonPath jsonPath = new JsonPath(response.asString());
		return jsonPath.getString("auth2AccessToken.access_token");
	}

	private void verify200OKResponse(Response response) {
		Assert.assertEquals(response.getStatusCode(), HttpStatus.SC_OK);
	}

	private Response callAPI(Method httpMethod, String path, Map<String, Object> payload) {
		switch (httpMethod) {
		case GET:
			return given().log().all().header("Authorization", token).header("X-TenantID", tenant)
					.header("Content-Type", "application/json").when().request(httpMethod.name(), path);
		case POST:
		case PUT:
		case DELETE:
			return given().log().all().header("Authorization", token).header("X-TenantID", tenant)
					.header("Content-Type", "application/json").with().body(payload).when()
					.request(httpMethod.name(), path);

		default:
			return null;
		}
	}

}