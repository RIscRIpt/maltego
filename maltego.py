#!/usr/bin/python

import sys

class Field:
	def __init__(self, name, display_name, rule, value):
		self.name = sanitise(name)
		self.display_name = sanitise(display_name)
		self.rule = rule
		self.value = value

class Entity:
	def __init__(self, entry_type: str = "maltego.Phrase", value: str = ""):
		self.entry_type = entry_type
		self.value = value
		self.weight = 100
		self.display_information = None
		self.additional_fields = []
		self.icon_url = ""
		self.properties = dict()

	def set_type(self, entry_type):
		self.entry_type = entry_type

	def set_value(self, value):
		self.value = sanitise(value)

	def set_weight(self, weight):
		self.weight = weight

	def set_display_information(self, display_information):
		self.display_information = display_information

	def add_field(self, name, display_name, rule=False, value=None):
		self.additional_fields.append(Field(
			name,
			display_name,
			rule,
			value
		))
	
	def add_property(self, key: str, value: str):
		self.properties[key] = value

	def set_icon_url(self, url):
		self.icon_url = url

	def __str__(self):
		properties = " "
		for key, value in self.properties.items():
			properties += f"{key}=\"{value}\" "
		result = f"""<Entity{properties}Type="{self.entry_type}">
	<Value>{self.value}</Value>
	<Weight>{self.weight}</Weight>
"""
		if self.display_information:
			result += f"""	<DisplayInformation>
		<Label Name="" Type="text/html"><![CDATA[{self.display_information}]]></Label>
	</DisplayInformation>
"""
		if self.additional_fields:
			result += "\t<AdditionalFields>\n"
			for field in self.additional_fields:
				rule = " "
				if field.rule != "strict":
					rule += "MatchingRule=\"" + str(field.rule) + "\""
					rule += " "
				result += "\t\t<Field" + rule + "Name=\"" + str(field.name) + "\" DisplayName=\"" + str(field.display_name) + "\">" + str(field.value) + "</Field>\n"
			result += "\t</AdditionalFields>\n"
		if self.icon_url:
			result += f"	<IconURL>{self.icon_url}</IconURL>\n"
		result += "</Entity>"
		return result

class UIMessage:
	def __init__(self, message_type, message):
		self.message_type = message_type
		self.message = message

class Transform:
	def __init__(self):
		self.value = ""
		self.values = dict()
		self.entities = []
		self.exceptions = []
		self.ui_messages = []

	def parse_arguments(self, argv):
		if len(argv) >= 2:
			self.value = argv[1]

		if len(argv) >= 3 and argv[2]:
			for var in argv[2].split("#"):
				values = var.split("=")
				if len(values) != 2:
					raise SyntaxError("invalid syntax of 3rd argument")
				self.values[values[0]] = values[1]

	def get_value(self) -> str:
		return self.value

	def get_variable(self, name: str) -> str:
		return self.values[name]

	def add_entity(self, e: Entity):
		self.entities.append(e)
		return self

	def add_ui_message(self, message: str, message_type = "Inform"):
		self.ui_messages.append(UIMessage(message_type, message))
		return self

	def add_exception(self, exception: str):
		self.exceptions.append(exception)
		return self

	def raise_exceptions(self):
		print("<MaltegoMessage>")
		print("\t<MaltegoTransformExceptionMessage>")
		print("\t\t<Exceptions>")
		for e in self.exceptions:
			print("\t\t\t<Exception>" + e + "</Exception>")
		print("\t\t</Exceptions>")
		print("\t</MaltegoTransformExceptionMessage>")
		print("</MaltegoMessage>")
		exit(1)

	def generate(self):
		print("<MaltegoMessage>")
		print("\t<MaltegoTransformResponseMessage>")
		print("\t\t<Entities>")
		for e in self.entities:
			print(tabulate(str(e), "\t\t\t"))
		print("\t\t</Entities>")
		print("\t\t<UIMessages>")
		for message in self.ui_messages:
			print("\t\t\t<UIMessage MessageType=\"" + message.message_type + "\">" + message.message + "</UIMessage>")
		print("\t\t</UIMessages>")
		print("\t</MaltegoTransformResponseMessage>")
		print("</MaltegoMessage>")
		exit(0)

	def _write_stderr(self, message: str):
		sys.stderr.write(message)
		sys.stderr.flush()

	def heartbeat(self):
		self._write_stderr("+")

	def progress(self, percent: int):
		self._write_stderr("%" + str(percent) + "\n")

	def debug(self, message: any):
		self._write_stderr("D:" + str(message) + "\n")

def sanitise(value: str) -> str:
	value = value.replace("&", "&amp;")
	value = value.replace("<", "&lt;")
	value = value.replace(">", "&gt;")
	return value

def tabulate(text: str, tab: str) -> str:
	lines = text.split("\n")
	lines = [tab + line for line in lines]
	return "\n".join(lines)
