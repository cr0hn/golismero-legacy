function loadConfigGeneral(){
	$.extend($.validity.messages, {
		require: i18n.t("validate.require"),

		// Format validators:
		match:"#{field} is in an invalid format.",
		integer:"#{field} must be a positive, whole number.",
		date:"#{field} must be formatted as a date.",
		email:"#{field} must be formatted as an email.",
		usd:"#{field} must be formatted as a US Dollar amount.",
		url:"#{field} must be formatted as a URL.",
		number:"#{field} must be formatted as a number.",
		zip:"#{field} must be formatted as a zipcode ##### or #####-####.",
		phone:"#{field} must be formatted as a phone number ###-###-####.",
		guid:"#{field} must be formatted as a guid like {3F2504E0-4F89-11D3-9A0C-0305E82C3301}.",
		time24:"#{field} must be formatted as a 24 hour time: 23:00.",
		time12:"#{field} must be formatted as a 12 hour time: 12:00 AM/PM",

		// Value range messages:
		lessThan:"#{field} must be less than #{max}.",
		lessThanOrEqualTo:"#{field} must be less than or equal to #{max}.",
		greaterThan:"#{field} must be greater than #{min}.",
		greaterThanOrEqualTo:"#{field} must be greater than or equal to #{min}.",
		range:"#{field} must be between #{min} and #{max}.",

		// Value length messages:
		tooLong:"#{field} cannot be longer than #{max} characters.",
		tooShort:"#{field} cannot be shorter than #{min} characters.}",

		// Aggregate validator messages:
		equal:"Values don't match.",
		distinct:"A value was repeated.",
		sum:"Values don't add to #{sum}.",
		sumMax:"The sum of the values must be less than #{max}.",
		sumMin:"The sum of the values must be greater than #{min}.",

		nonHtml:"#{field} cannot contain Html characters.",

		generic:"Invalid."
	});
}