package com.eka.ekaconnect.controllers;

import static io.restassured.RestAssured.given;
import static org.hamcrest.CoreMatchers.is;
import static org.hamcrest.Matchers.containsString;

import java.io.File;
import java.io.FileInputStream;
import java.io.UnsupportedEncodingException;
import java.net.URL;
import java.util.Base64;
import java.util.HashMap;
import java.util.Map;
import java.util.Properties;

import org.json.JSONObject;
import org.springframework.util.ResourceUtils;
import org.testng.Assert;
import org.testng.annotations.BeforeTest;
import org.testng.annotations.Test;

import io.restassured.RestAssured;
import io.restassured.path.json.JsonPath;
import io.restassured.response.Response;

public class AppDataControllerTest {

	String token = null;
	String tenant = null;
	String userName = null;
	String password = null;
	Map<String, Object> requestPayload = new HashMap<String, Object>();

	private static final String tokenGenerationApiPath = "/api/authenticate";

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
	public void testDeletingToSetStateToDelete() {
		// save order object data--
		Response saveDataResponse = given().log().all().header("Authorization", token).header("X-TenantID", tenant)
				.header("Content-Type", "application/json").with().body(payloadToSaveData()).when()
				.request("POST", "/data/e621d081-85cb-4951-adea-49b88d7f4ab0/8ca20157-5616-41ec-9fb5-fe8a733c948b");
		JsonPath jsonPathForSavedData = new JsonPath(saveDataResponse.asString());
		Object _id = null;
		_id = jsonPathForSavedData.get("_id");
		Assert.assertEquals(jsonPathForSavedData.get("sys__data__state"), "Create");
		// delete this data--
		given().log().all().header("Authorization", token).header("X-TenantID", tenant)
				.header("Content-Type", "application/json").when()
				.request("DELETE",
						"/data/e621d081-85cb-4951-adea-49b88d7f4ab0/8ca20157-5616-41ec-9fb5-fe8a733c948b/" + _id)
				.then().assertThat().statusCode(200);
		// fetch deleted documents--
		given().log().all().header("Authorization", token).header("X-TenantID", tenant)
				.header("Content-Type", "application/json").when()
				.request("GET",
						"/data/e621d081-85cb-4951-adea-49b88d7f4ab0/8ca20157-5616-41ec-9fb5-fe8a733c948b/deleted")
				.then().assertThat().statusCode(200).body(containsString(_id.toString()))
				.body(containsString("\"sys__data__state\":\"Delete\""));
	}
	
	@Test(enabled = true)
	public void testDeletingAlreadyDeletedData() {
		// save order object data--
		Response saveDataResponse = given().log().all().header("Authorization", token).header("X-TenantID", tenant)
				.header("Content-Type", "application/json").with().body(payloadToSaveData()).when()
				.request("POST", "/data/e621d081-85cb-4951-adea-49b88d7f4ab0/8ca20157-5616-41ec-9fb5-fe8a733c948b");
		JsonPath jsonPathForSavedData = new JsonPath(saveDataResponse.asString());
		Object _id = null;
		_id = jsonPathForSavedData.get("_id");

		// delete this data--
		given().log().all().header("Authorization", token).header("X-TenantID", tenant)
				.header("Content-Type", "application/json").when()
				.request("DELETE",
						"/data/e621d081-85cb-4951-adea-49b88d7f4ab0/8ca20157-5616-41ec-9fb5-fe8a733c948b/" + _id)
				.then().assertThat().statusCode(200);
		// delete this data again
		given().log().all().header("Authorization", token).header("X-TenantID", tenant)
				.header("Content-Type", "application/json").when()
				.request("DELETE",
						"/data/e621d081-85cb-4951-adea-49b88d7f4ab0/8ca20157-5616-41ec-9fb5-fe8a733c948b/" + _id)
				.then().assertThat().statusCode(400)
				.body("errorLocalizedMessage", containsString("Object is not availiable"));
	}
	
	@Test(enabled = true)
	public void testListDeletedDataAPI() {
		given().log().all().header("Authorization", token).header("X-TenantID", tenant)
				.header("Content-Type", "application/json").when()
				.request("GET",
						"/data/d33143ac-4164-4a3f-8d30-61d845c9eeed/00189ca9-cfc1-4327-95ac-f937f22deb60/deleted")
				.then().assertThat().statusCode(200).body("[0].sys__data__state", is("Delete"));
	}
	
	@Test(enabled = true)
	public void testSaveDataAPI() {
		given().log().all().header("Authorization", token).header("X-TenantID", tenant)
				.header("Content-Type", "application/json").with().body(bodyForSaveDataApi().toString()).when()
				.request("POST", "/data/467a28cc-bc93-4e38-8ff5-0a56ae128f3b/c05cacf5-200c-4d97-8e8d-a67329ff286c")
				.then().assertThat().statusCode(200);
	}
	
	private Map<String,Object> payloadToSaveData(){
		String payloadString = "{\"sourceId\":\"143\",\"orderType\":\"Limited\",\"instrumentType\":\"FUT\",\"orderNo\":\"53\",\"triggerPrice\":\"\",\"limitPrice\":\"3\",\"orderStatus\":\"Replace\",\"instrument\":\"CBOT Corn Futuresstttgggghhfggghh\",\"source\":\"\",\"tradeDate\":\"21-Mar-2019\",\"broker\":\"RJ O'Brien\",\"expirtyDate\":\"Invalid date\",\"filledQuantity\":\"\",\"orderQuantity\":467,\"promptMonth\":\"Dec-2019\",\"instrumentDetails\":\"xy\",\"counterParty\":\"\",\"timeInForce\":\"DayNight\",\"account\":\"rs365561\",\"tradeType\":\"Sell\",\"strikePrice\":\"\",\"sys__state\":\"any state\"}";
		JSONObject payloadJson = new JSONObject(payloadString);
		return payloadJson.toMap();
	}
	
	@Test(enabled = true)
	public void testSaveDataAPIToCheckVersionStructure() {
		// save order object data--
		Response saveDataResponse = given().log().all().header("Authorization", token).header("X-TenantID", tenant)
				.header("Content-Type", "application/json").with().body(payloadToSaveData()).when()
				.request("POST", "/data/e621d081-85cb-4951-adea-49b88d7f4ab0/8ca20157-5616-41ec-9fb5-fe8a733c948b");
		JsonPath jsonPathForSavedData = new JsonPath(saveDataResponse.asString());
		Object _id = null;
		Object sys__UUID = null;
		_id = jsonPathForSavedData.get("_id");
		sys__UUID = jsonPathForSavedData.get("sys__UUID");
		// fetch version document--
		given().log().all().header("Authorization", token).header("X-TenantID", tenant)
				.header("Content-Type", "application/json").when()
				.request("GET",
						"/workflow/e621d081-85cb-4951-adea-49b88d7f4ab0/_UT_VIEW_VERSION_HISTORY/data/" + sys__UUID
								+ "/versions")
				.then().assertThat().statusCode(200).body("refType", is("objectData")).body("refTypeId", is(sys__UUID))
				.body("app_UUID", is("e621d081-85cb-4951-adea-49b88d7f4ab0"));
	}

	@Test(enabled = true)
	public void testSaveDataValidationFailedAPIWhenMendatoryFieldNotExist() {
		given().log().all().header("Authorization", token).header("X-TenantID", tenant)
				.header("Content-Type", "application/json").with()
				.body(bodyForSaveDataWithValidationFailedApiWhenMendatoryFieldNotExist().toString()).when()
				.request("POST", "/data/467a28cc-bc93-4e38-8ff5-0a56ae128f3b/c05cacf5-200c-4d97-8e8d-a67329ff286c")
				.then().assertThat().statusCode(400)
				.body("errorLocalizedMessage", is("Please fill all the required fields appropriately."))
				.body("errors[0].errorContext", is("{field:SupplierReference}")).body("errors[0].errorLocalizedMessage", is("mandatoryField"));
	}
	
	@Test(enabled = true)
	public void testSaveDataValidationFailedAPIWhenUnkownFieldExist() {
		given().log().all().header("Authorization", token).header("X-TenantID", tenant)
				.header("Content-Type", "application/json").with()
				.body(bodyForSaveDataWithValidationFailedApiWhenUnkownFieldExist().toString()).when()
				.request("POST", "/data/467a28cc-bc93-4e38-8ff5-0a56ae128f3b/c05cacf5-200c-4d97-8e8d-a67329ff286c")
				.then().assertThat().statusCode(400)
				.body("errorLocalizedMessage", is("Please fill all the required fields appropriately."))
				.body("errors[0].errorContext", is("{field:pin}"))
				.body("errors[0].errorLocalizedMessage", is("pin field is invalid"));
	}

	@Test(enabled = true)
	public void testSaveDatalengthValidationFailedAPI() {
		given().log().all().header("Authorization", token).header("X-TenantID", tenant)
				.header("Content-Type", "application/json").with()
				.body(bodyForSaveDataWithlengthValidationFailed().toString()).when()
				.request("POST", "/data/467a28cc-bc93-4e38-8ff5-0a56ae128f3b/c05cacf5-200c-4d97-8e8d-a67329ff286c")
				.then().assertThat().statusCode(400)
				.body("errorLocalizedMessage", is("Please fill all the required fields appropriately."))
				.body("errors[0].errorContext", is("{field:deliveryItemRefNo}"))
				.body("errors[0].errorLocalizedMessage", is("deliveryItemRefNo length must be less than 20"));
	}
	
	private JSONObject bodyForSaveDataWithValidationFailedApiWhenUnkownFieldExist() {
		JSONObject requestBody = new JSONObject();
		requestBody.put("pcdiId", "PHD");
		requestBody.put("LoadingLocationCity", "BNG");
		requestBody.put("CountryOfOrigin", "INDIA");
		requestBody.put("LoadingLocationCountry", "INDIA");
		requestBody.put("Quality", "GOOD");
		requestBody.put("MaterialDescription", "SOLID");
		requestBody.put("SupplierReference", "PHD");
		requestBody.put("ExpectedArrivalDate", "2020-11-08");
		requestBody.put("LoadingDate", "2020-11-01");
		requestBody.put("incoLocation", "INDIA");
		requestBody.put("containerFlag", "YES");
		requestBody.put("pin", "0123");
		return requestBody;
	}

	private JSONObject bodyForSaveDataWithlengthValidationFailed() {
		JSONObject requestBody = new JSONObject();
		requestBody.put("pcdiId", "PHD");
		requestBody.put("LoadingLocationCity", "BNG");
		requestBody.put("CountryOfOrigin", "INDIA");
		requestBody.put("LoadingLocationCountry", "INDIA");
		requestBody.put("Quality", "GOOD");
		requestBody.put("MaterialDescription", "SOLID");
		requestBody.put("SupplierReference", "PHD");
		requestBody.put("ExpectedArrivalDate", "2020-11-08");
		requestBody.put("LoadingDate", "2020-11-01");
		requestBody.put("incoLocation", "INDIA");
		requestBody.put("containerFlag", "YES");
		requestBody.put("deliveryItemRefNo", "lenghthFreaterThanTwentyIsNotValid");
		return requestBody;
	}
	
	private JSONObject bodyForSaveDataApi() {
		JSONObject requestBody = new JSONObject();
		requestBody.put("pcdiId", "PHD");
		requestBody.put("LoadingLocationCity", "BNG");
		requestBody.put("CountryOfOrigin", "INDIA");
		requestBody.put("LoadingLocationCountry", "INDIA");
		requestBody.put("Quality", "GOOD");
		requestBody.put("MaterialDescription", "SOLID");
		requestBody.put("SupplierReference", "PHD");
		requestBody.put("ExpectedArrivalDate", "2020-11-08");
		requestBody.put("LoadingDate", "2020-11-01");
		requestBody.put("incoLocation", "INDIA");
		requestBody.put("containerFlag", "YES");
		return requestBody;
	}
	
	private JSONObject bodyForSaveDataWithValidationFailedApiWhenMendatoryFieldNotExist() {
		JSONObject requestBody = new JSONObject();
		requestBody.put("pcdiId", "PHD");
		requestBody.put("LoadingLocationCity", "BNG");
		requestBody.put("CountryOfOrigin", "INDIA");
		requestBody.put("LoadingLocationCountry", "INDIA");
		requestBody.put("Quality", "GOOD");
		requestBody.put("MaterialDescription", "SOLID");
		requestBody.put("ExpectedArrivalDate", "2020-11-08");
		requestBody.put("LoadingDate", "2020-11-01");
		requestBody.put("incoLocation", "INDIA");
		requestBody.put("containerFlag", "YES");
		return requestBody;
	}
	
	private String authenticateUser(String username, String password) throws UnsupportedEncodingException {
		Map<String, Object> reqBody = new HashMap<String, Object>();
		reqBody.put("userName", username);
		reqBody.put("pwd", password);
		String base64encodedUsernamePassword = Base64.getEncoder()
				.encodeToString((username + ":" + password).getBytes("utf-8"));
		Response response = given().header("Content-Type", "application/json")
				.header("Authorization", "Basic " + base64encodedUsernamePassword).header("X-TenantID", tenant)
				.body(reqBody).when().post(tokenGenerationApiPath);
		JsonPath jsonPath = new JsonPath(response.asString());
		return jsonPath.getString("auth2AccessToken.access_token");
	}
}
