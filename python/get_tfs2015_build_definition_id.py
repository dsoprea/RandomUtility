import logging
import os.path
import json

_LOGGER = logging.getLogger(__name__)


class Tfs(object):
	def __init__(self, agent_path):
		self.__agent_path = agent_path
		self.__srm_path = \
			os.path.join(
				self.__agent_path, 
				'_work', 
				'SourceRootMapping')

		_LOGGER.debug("Agent SRM path: [%s]", self.__srm_path)

	def collection_gen(self):
		for filename in os.listdir(self.__srm_path):
			filepath = os.path.join(self.__srm_path, filename)
			if os.path.isdir(filepath) is False:
				continue

			_LOGGER.debug("Collection GUID: [%s]", filename)
			yield filename, filepath

	def definition_gen(self, collection_path):
		for srm_id_raw in os.listdir(collection_path):
			_LOGGER.debug("SRM ID: [%s]", srm_id_raw)

			definition_info_filepath = \
				os.path.join(
					collection_path, 
					srm_id_raw, 
					'SourceFolder.json')

			with open(definition_info_filepath) as f:
				yield json.load(f)

	def lookup_definition(self, definition_name):
		for collection_guid, collection_path in self.collection_gen():
			for definition in self.definition_gen(collection_path):
				current_definition_name = definition['definitionName']
				_LOGGER.debug("Definition: [%s]", current_definition_name)

				if current_definition_name != definition_name:
					continue

				return definition

		raise ValueError("Could not find definition: {}".format(
						 definition_name))


def _configure_logging():
    sh = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s [%(name)s %(levelname)s] %(message)s')
    sh.setFormatter(formatter)

    _LOGGER.addHandler(sh)
    _LOGGER.setLevel(logging.DEBUG)

if __name__ == '__main__':
	import argparse

	parser = argparse.ArgumentParser()

	parser.add_argument(
		'agent_path', 
		help="Agent path")

	parser.add_argument(
		'definition_name', 
		help="Build-definition name")

	args = parser.parse_args()

	_configure_logging()

	t = Tfs(args.agent_path)
	definition = t.lookup_definition(args.definition_name)

	print(definition['agent_builddirectory'])
