package com.eka.ekaconnect.apps;

import static io.restassured.RestAssured.given;
import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.CoreMatchers.instanceOf;
import static org.hamcrest.CoreMatchers.is;
import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.greaterThan;

import java.io.FileInputStream;
import java.io.UnsupportedEncodingException;
import java.net.URL;
import java.util.Base64;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Properties;

import org.apache.http.HttpStatus;
import org.json.JSONObject;
import org.springframework.util.ResourceUtils;
import org.testng.Assert;
import org.testng.annotations.BeforeTest;
import org.testng.annotations.Test;

import io.restassured.RestAssured;
import io.restassured.http.Method;
import io.restassured.path.json.JsonPath;
import io.restassured.response.Response;

public class SupplierConnect {

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
	public void testListPageAPIs() {
		// call app meta--
		Response appMetaResponse = callAPI(Method.POST, "/meta/app/power", new HashMap<>());
		verify200OKResponse(appMetaResponse);
		appMetaResponse.then().assertThat().body("name", is("power"));
		// call layout--
		String layoutCallPayloadString = "{\"appId\":\"d7d05837-88a3-471e-a5f1-1c5fd6cec3e7\",\"workFlowTask\":\"powerlisting\",\"payLoadData\":\"\"}";
		Response layoutResponse = callAPI(Method.POST, "/workflow/layout",
				generatePayloadFromString(layoutCallPayloadString));
		verify200OKResponse(layoutResponse);
		layoutResponse.then().assertThat().body("appId", is("d7d05837-88a3-471e-a5f1-1c5fd6cec3e7"));
		// call data--
		String dataCallPayloadString = "{\"appId\":\"d7d05837-88a3-471e-a5f1-1c5fd6cec3e7\",\"workFlowTask\":\"powerlisting\"}";
		Response dataResponse = callAPI(Method.POST, "/workflow/data",
				generatePayloadFromString(dataCallPayloadString));
		verify200OKResponse(dataResponse);
		dataResponse.then().assertThat().body("data.size()", greaterThan(0));
	}

	@Test(enabled = true)
	public void testGeneralDetailsPageAPIs() {
		// call layout--
		String layoutCallPayloadString = "{\"appId\":\"d7d05837-88a3-471e-a5f1-1c5fd6cec3e7\",\"workFlowTask\":\"createTrade_PNG\",\"payLoadData\":\"\"}";
		Response layoutResponse = callAPI(Method.POST, "/workflow/layout",
				generatePayloadFromString(layoutCallPayloadString));
		verify200OKResponse(layoutResponse);
		layoutResponse.then().assertThat().body("appId", is("d7d05837-88a3-471e-a5f1-1c5fd6cec3e7"));
		
		// call workflow save--
		String dataCallPayloadString = "{\"workflowTaskName\":\"createTrade_PNG\",\"task\":\"createTrade_PNG\",\"appName\":\"power\",\"appId\":\"d7d05837-88a3-471e-a5f1-1c5fd6cec3e7\",\"output\":{\"createTrade_PNG\":{\"sys__state\":{\"powerContractRefNo\":{\"show\":true,\"disable\":false},\"selectTemplate\":{\"show\":true,\"disable\":false},\"product\":{\"show\":true,\"disable\":false},\"contractType\":{\"show\":true,\"disable\":false},\"dealType\":{\"show\":true,\"disable\":false},\"contractIssueDate\":{\"show\":true,\"disable\":false},\"traderName\":{\"show\":true,\"disable\":false},\"cpName\":{\"show\":true,\"disable\":false},\"paymentTerms\":{\"show\":true,\"disable\":false},\"payInSettlementCurrency\":{\"show\":true,\"disable\":false},\"paymentDueDate\":{\"show\":true,\"disable\":false},\"profitCenter\":{\"show\":true,\"disable\":false},\"strategy\":{\"show\":true,\"disable\":false},\"pdSchedule\":{\"show\":true,\"disable\":false},\"applicableLawContract\":{\"show\":true,\"disable\":false},\"arbitration\":{\"show\":true,\"disable\":false},\"timeZone\":{\"show\":true,\"disable\":false},\"holidayCalendar\":{\"show\":true,\"disable\":false},\"borkerName\":{\"show\":true,\"disable\":false},\"brokerPersonIncharge\":{\"show\":true,\"disable\":false},\"brokerRefNo\":{\"show\":true,\"disable\":false},\"brokerCommission\":{\"show\":true,\"disable\":false},\"brokerCommissionUnit\":{\"show\":true,\"disable\":false},\"cpPersonIncharge\":{\"show\":true,\"disable\":false},\"cpContractRefNo\":{\"show\":true,\"disable\":false},\"remark\":{\"show\":true,\"disable\":false},\"deliveryType\":{\"show\":true,\"disable\":false},\"priceType\":{\"show\":true,\"disable\":false},\"quantityUnit\":{\"show\":true,\"disable\":false},\"priceUnit\":{\"show\":true,\"disable\":false},\"deliveryDetails\":{\"show\":true,\"disable\":false},\"userId\":{\"show\":true,\"disable\":false},\"sys__createdBy\":{\"show\":true,\"disable\":false},\"sys__createdOn\":{\"show\":true,\"disable\":false},\"productDisplayName\":{\"show\":true,\"disable\":false},\"contractTypeDisplayName\":{\"show\":true,\"disable\":false},\"dealTypeDisplayName\":{\"show\":true,\"disable\":false},\"traderNameDisplayName\":{\"show\":true,\"disable\":false},\"cpNameDisplayName\":{\"show\":true,\"disable\":false},\"paymentTermsDisplayName\":{\"show\":true,\"disable\":false},\"payInSettlementCurrencyDisplayName\":{\"show\":true,\"disable\":false},\"profitCenterDisplayName\":{\"show\":true,\"disable\":false},\"strategyDisplayName\":{\"show\":true,\"disable\":false},\"valuationFormulaId\":{\"show\":true,\"disable\":false}},\"product\":\"PDM-4751\",\"contractType\":\"P\",\"dealType\":\"Third_Party\",\"contractIssueDate\":\"2020-02-25\",\"traderName\":\"AK-2057\",\"productDisplayName\":\"Crude\",\"contractTypeDisplayName\":\"Purchase\",\"dealTypeDisplayName\":\"Third Party\",\"traderNameDisplayName\":\"Aftab P\"}},\"id\":\"\"}";

		Response dataResponse = callAPI(Method.POST, "/workflow",
				generatePayloadFromString(dataCallPayloadString));
		verify200OKResponse(dataResponse);
		dataResponse.then().assertThat().body("data.size()", greaterThan(0));
	}

	@Test(enabled = true)
	public void testDeliveryDetailsPageAPIs() {
		// call layout--
		String layoutCallPayloadString = "{\"appId\":\"d7d05837-88a3-471e-a5f1-1c5fd6cec3e7\",\"workFlowTask\":\"deliveryDetails_PNG\",\"payLoadData\":{\"product\":\"PDM-4751\",\"sys__data__state\":\"Create\",\"contractType\":\"P\",\"refType\":\"app\",\"refTypeId\":\"d7d05837-88a3-471e-a5f1-1c5fd6cec3e7\",\"traderNameDisplayName\":\"Aftab P\",\"dealType\":\"Third_Party\",\"userId\":\"3142\",\"powerContractRefNo\":\"PW-84-REF\",\"sys__state\":{\"brokerRefNo\":{\"disable\":false,\"show\":true},\"brokerCommissionUnit\":{\"disable\":false,\"show\":true},\"profitCenterDisplayName\":{\"disable\":false,\"show\":true},\"strategyDisplayName\":{\"disable\":false,\"show\":true},\"contractType\":{\"disable\":false,\"show\":true},\"remark\":{\"disable\":false,\"show\":true},\"quantityUnit\":{\"disable\":false,\"show\":true},\"traderNameDisplayName\":{\"disable\":false,\"show\":true},\"profitCenter\":{\"disable\":false,\"show\":true},\"valuationFormulaId\":{\"disable\":false,\"show\":true},\"powerContractRefNo\":{\"disable\":false,\"show\":true},\"brokerCommission\":{\"disable\":false,\"show\":true},\"borkerName\":{\"disable\":false,\"show\":true},\"payInSettlementCurrency\":{\"disable\":false,\"show\":true},\"dealTypeDisplayName\":{\"disable\":false,\"show\":true},\"applicableLawContract\":{\"disable\":false,\"show\":true},\"deliveryDetails\":{\"disable\":false,\"show\":true},\"holidayCalendar\":{\"disable\":false,\"show\":true},\"contractTypeDisplayName\":{\"disable\":false,\"show\":true},\"paymentTermsDisplayName\":{\"disable\":false,\"show\":true},\"paymentTerms\":{\"disable\":false,\"show\":true},\"priceUnit\":{\"disable\":false,\"show\":true},\"product\":{\"disable\":false,\"show\":true},\"cpPersonIncharge\":{\"disable\":false,\"show\":true},\"cpName\":{\"disable\":false,\"show\":true},\"deliveryType\":{\"disable\":false,\"show\":true},\"priceType\":{\"disable\":false,\"show\":true},\"timeZone\":{\"disable\":false,\"show\":true},\"selectTemplate\":{\"disable\":false,\"show\":true},\"dealType\":{\"disable\":false,\"show\":true},\"cpContractRefNo\":{\"disable\":false,\"show\":true},\"arbitration\":{\"disable\":false,\"show\":true},\"userId\":{\"disable\":false,\"show\":true},\"cpNameDisplayName\":{\"disable\":false,\"show\":true},\"brokerPersonIncharge\":{\"disable\":false,\"show\":true},\"paymentDueDate\":{\"disable\":false,\"show\":true},\"contractIssueDate\":{\"disable\":false,\"show\":true},\"sys__createdBy\":{\"disable\":false,\"show\":true},\"pdSchedule\":{\"disable\":false,\"show\":true},\"productDisplayName\":{\"disable\":false,\"show\":true},\"strategy\":{\"disable\":false,\"show\":true},\"sys__createdOn\":{\"disable\":false,\"show\":true},\"payInSettlementCurrencyDisplayName\":{\"disable\":false,\"show\":true},\"traderName\":{\"disable\":false,\"show\":true}},\"contractIssueDate\":\"0030-08-13T05:30:00.000+05:30\",\"dealTypeDisplayName\":\"Third Party\",\"sys__createdBy\":\"admin@ekaplus.com\",\"productDisplayName\":\"Crude\",\"_id\":\"5e3bb8516522050001ae4b65\",\"contractTypeDisplayName\":\"Purchase\",\"sys__createdOn\":\"Thu Feb 06 06:55:13 UTC 2020\",\"traderName\":\"AK-2057\",\"object\":\"73314f69-35dc-43c1-a1db-47d755bafd0d\",\"sys__UUID\":\"801a1247-26b4-45a7-aab1-a444d00c2645\"}}";
		Response layoutResponse = callAPI(Method.POST, "/workflow/layout",
				generatePayloadFromString(layoutCallPayloadString));
		verify200OKResponse(layoutResponse);
		layoutResponse.then().assertThat().body("appId", is("d7d05837-88a3-471e-a5f1-1c5fd6cec3e7"));
		
		// call save ItemDetails Block--
		String dataCallPayloadString = "{\"workflowTaskName\":\"itemDetails_PNG\",\"task\":\"itemDetails_PNG\",\"appName\":\"power\",\"appId\":\"d7d05837-88a3-471e-a5f1-1c5fd6cec3e7\",\"output\":{\"itemDetails_PNG\":[{\"blockNo\":1,\"startDate\":\"24-02-2020\",\"startDateDatePicker\":\"2020-02-23T18:30:00.000Z\",\"endDate\":\"27-02-2020\",\"endDateDatePicker\":\"2020-02-26T18:30:00.000Z\",\"startTime\":\"08:00\",\"startTimeTimePicker\":\"2020-02-06T02:30:00.636Z\",\"endTime\":\"20:00\",\"endTimeTimePicker\":\"2020-02-06T14:30:00.664Z\",\"weekDays\":{\"Sunday\":true,\"Monday\":true,\"Tuesday\":true,\"Wednesday\":true,\"Friday\":true,\"Saturday\":true,\"Holiday\":true},\"quantity\":400,\"transmissionLoss\":\"+ Add Loss\",\"secondaryCost\":\"+ Add Cost\",\"hoursPerDay\":12,\"quantityPerDay\":4800,\"totalDays\":3,\"totalHours\":36,\"totalQuantity\":14400,\"totalAmount\":17280000,\"price\":1200,\"powerContractRefNo\":\"PW-85-REF\"}]}}";
		Response dataResponse = callAPI(Method.POST, "/workflow",
				generatePayloadFromString(dataCallPayloadString));
		verify200OKResponse(dataResponse);
		dataResponse.then().assertThat().body("data.size()", greaterThan(0));

		// call update generalDetails
		String updateGeneralDetailsPayloadString = "{\"workflowTaskName\":\"deliveryDetails_PNG\",\"task\":\"deliveryDetails_PNG\",\"appName\":\"power\",\"appId\":\"d7d05837-88a3-471e-a5f1-1c5fd6cec3e7\",\"output\":{\"deliveryDetails_PNG\":{\"product\":\"PDM-4751\",\"sys__data__state\":\"Create\",\"contractType\":\"S\",\"refType\":\"app\",\"refTypeId\":\"d7d05837-88a3-471e-a5f1-1c5fd6cec3e7\",\"traderNameDisplayName\":\"Aftab P\",\"dealType\":\"Third_Party\",\"userId\":\"3142\",\"powerContractRefNo\":\"PW-85-REF\",\"sys__state\":{\"brokerRefNo\":{\"disable\":false,\"show\":true},\"brokerCommissionUnit\":{\"disable\":false,\"show\":true},\"profitCenterDisplayName\":{\"disable\":false,\"show\":true},\"strategyDisplayName\":{\"disable\":false,\"show\":true},\"contractType\":{\"disable\":false,\"show\":true},\"remark\":{\"disable\":false,\"show\":true},\"quantityUnit\":{\"disable\":false,\"show\":true},\"traderNameDisplayName\":{\"disable\":false,\"show\":true},\"profitCenter\":{\"disable\":false,\"show\":true},\"valuationFormulaId\":{\"disable\":false,\"show\":true},\"powerContractRefNo\":{\"disable\":false,\"show\":true},\"brokerCommission\":{\"disable\":false,\"show\":true},\"borkerName\":{\"disable\":false,\"show\":true},\"payInSettlementCurrency\":{\"disable\":false,\"show\":true},\"dealTypeDisplayName\":{\"disable\":false,\"show\":true},\"applicableLawContract\":{\"disable\":false,\"show\":true},\"deliveryDetails\":{\"disable\":false,\"show\":true},\"holidayCalendar\":{\"disable\":false,\"show\":true},\"contractTypeDisplayName\":{\"disable\":false,\"show\":true},\"paymentTermsDisplayName\":{\"disable\":false,\"show\":true},\"paymentTerms\":{\"disable\":false,\"show\":true},\"priceUnit\":{\"disable\":false,\"show\":true},\"product\":{\"disable\":false,\"show\":true},\"cpPersonIncharge\":{\"disable\":false,\"show\":true},\"cpName\":{\"disable\":false,\"show\":true},\"deliveryType\":{\"disable\":false,\"show\":true},\"priceType\":{\"disable\":false,\"show\":true},\"timeZone\":{\"disable\":false,\"show\":true},\"selectTemplate\":{\"disable\":false,\"show\":true},\"dealType\":{\"disable\":false,\"show\":true},\"cpContractRefNo\":{\"disable\":false,\"show\":true},\"arbitration\":{\"disable\":false,\"show\":true},\"userId\":{\"disable\":false,\"show\":true},\"cpNameDisplayName\":{\"disable\":false,\"show\":true},\"brokerPersonIncharge\":{\"disable\":false,\"show\":true},\"paymentDueDate\":{\"disable\":false,\"show\":true},\"contractIssueDate\":{\"disable\":false,\"show\":true},\"sys__createdBy\":{\"disable\":false,\"show\":true},\"pdSchedule\":{\"disable\":false,\"show\":true},\"productDisplayName\":{\"disable\":false,\"show\":true},\"strategy\":{\"disable\":false,\"show\":true},\"sys__createdOn\":{\"disable\":false,\"show\":true},\"payInSettlementCurrencyDisplayName\":{\"disable\":false,\"show\":true},\"traderName\":{\"disable\":false,\"show\":true}},\"contractIssueDate\":\"0031-08-13T05:30:00.000+05:30\",\"dealTypeDisplayName\":\"Third Party\",\"sys__createdBy\":\"admin@ekaplus.com\",\"productDisplayName\":\"Crude\",\"_id\":\"5e3bbb1f6522050001ae4b77\",\"contractTypeDisplayName\":\"Sale\",\"sys__createdOn\":\"Thu Feb 06 07:07:11 UTC 2020\",\"traderName\":\"AK-2057\",\"object\":\"73314f69-35dc-43c1-a1db-47d755bafd0d\",\"sys__UUID\":\"c66bbc49-6358-48a2-b2ce-966c7cfaeb15\",\"priceType\":\"Fixed\",\"priceUnit\":\"USD\",\"quantityUnit\":\"MWh\",\"deliveryType\":\"Block\",\"valuationFormulaId\":null}},\"id\":\"5e3bbb1f6522050001ae4b77\"}";
		Response updateResponse = callAPI(Method.POST, "/workflow",
				generatePayloadFromString(updateGeneralDetailsPayloadString));
		verify200OKResponse(dataResponse);
		updateResponse.then().assertThat().body("data.sys__data__state", "Modify");
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
		}
		return null;
	}

	private Map<String, Object> generatePayloadFromString(String payload) {
		return new JSONObject(payload).toMap();
	}

	private void verify200OKResponse(Response response) {
		Assert.assertEquals(response.getStatusCode(), HttpStatus.SC_OK);
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
