// passkey_login_translations.test.js — guest catalog loader wiring.
// Runs without bench/jsdom through the login bundle's Node test seam.

const test = require("node:test");
const assert = require("node:assert");

const C = require("../../public/js/passkey_common.bundle.js");

global.document = {
	readyState: "loading",
	addEventListener() {},
};

let request;
global.fetch = function (url, options) {
	request = { url, options };
	return Promise.resolve({
		ok: true,
		json() {
			return Promise.resolve({ message: { "Sign in with a passkey": "Connexion avec une clé" } });
		},
	});
};

global.window = {
	frappe: {
		passkeys_common: C,
		_messages: { "Core label": "Libellé principal" },
		_translations_loaded: Promise.resolve(),
	},
	addEventListener() {},
};

const mod = require("../../public/js/passkey_login.bundle.js");

test("translation loader bypasses caches and merges the returned app catalog", async () => {
	await mod.loadAppTranslations();

	assert.strictEqual(request.url, "/api/method/passkeys.passkey.get_app_translations");
	assert.strictEqual(request.options.method, "GET");
	assert.strictEqual(request.options.cache, "no-store");
	assert.strictEqual(window.frappe._messages["Core label"], "Libellé principal");
	assert.strictEqual(
		window.frappe._messages["Sign in with a passkey"],
		"Connexion avec une clé",
	);
});
