package com.eka.ekaconnect.controllers;

import static io.restassured.RestAssured.given;
import static org.hamcrest.CoreMatchers.is;
import static org.hamcrest.Matchers.containsString;

import java.io.FileInputStream;
import java.io.UnsupportedEncodingException;
import java.net.URL;
import java.util.Base64;
import java.util.HashMap;
import java.util.Map;
import java.util.Properties;

import org.json.JSONObject;
import org.springframework.util.ResourceUtils;
import org.testng.annotations.BeforeTest;
import org.testng.annotations.Test;

import io.restassured.RestAssured;
import io.restassured.path.json.JsonPath;
import io.restassured.response.Response;

public class LoginControllerTest {

	String token = null;
	String tenant = null;
	String userName = null;
	String password = null;
	Map<String, Object> requestPayload = new HashMap<String, Object>();

	private static final String tokenGenerationApiPath = "/api/authenticate";
	private static final String validateNewPassWordApiPath = "/authenticate/validateNewPassword";

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

	@Test(enabled = true)
	public void testValidateNewPassword() {
		String payloadString = "{\"pwd\":\"hi43434\",\"userName\":\"Bravo\"}";
		JSONObject payloadJson = new JSONObject(payloadString);

		given().log().all().header("Authorization", token).header("X-TenantID", tenant)
				.header("Content-Type", "application/json").with().body(payloadJson.toMap()).when()
				.request("POST", validateNewPassWordApiPath).then().assertThat().statusCode(200)
				.body("seccessMessage", is("Valid Password"));
	}

	@Test(enabled = true)
	public void testValidateNewPasswordWithoutToken() {
		String payloadString = "{\"pwd\":\"hi43434\",\"userName\":\"Bravo\"}";
		JSONObject payloadJson = new JSONObject(payloadString);

		given().log().all().header("X-TenantID", tenant).header("Content-Type", "application/json").with()
				.body(payloadJson.toMap()).when().request("POST", validateNewPassWordApiPath).then().assertThat()
				.statusCode(400).body("errorLocalizedMessage", containsString("401 Unauthorized"));
	}

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
