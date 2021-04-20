
from utilities.transformer import Transformer
from utilities import logger
from product_types.base_variable import BaseVariable

class Variable(BaseVariable):

    def __init__(self, variable_data, parent_product, parent_datastructure = None, parent_varset = None):
        super().__init__(parent_product)
        self.product_type = parent_product.product_type
        self.parent_varset = parent_varset
        self.parent_datastructure = parent_datastructure
        self.name = self.transformer.cleanup_html_encoding(variable_data.get("Variable Name"))
        self.label = self.transformer.cleanup_html_encoding(variable_data.get("Variable Label"))
        self.data_type =self.transformer.cleanup_html_encoding(variable_data.get("Type"))
        self.ordinal = str(self.transformer.cleanup_html_encoding(variable_data.get("Seq. for Order")))
        self.description = self.transformer.cleanup_html_encoding(variable_data.get("CDISC Notes"))
        self.core = self.transformer.cleanup_html_encoding(variable_data.get("Core"))
        self.parent_datastructure_name = self.transformer.cleanup_html_encoding(variable_data.get("Class", variable_data.get("Dataset Name")).strip())
        if self.parent_product.product_type != "adamig" and not self.parent_datastructure_name:
            self.parent_datastructure_name = self.parent_product.product_type.split("-")[-1].upper()
        self.parent_varset_name = variable_data.get("Variable Grouping", "").strip()
        self.codelist = self.transformer.cleanup_html_encoding(variable_data.get("Codelist/Controlled Terms", variable_data.get("Codelist")))
        self.controlled_terms = self.transformer.cleanup_html_encoding(variable_data.get("Controlled Terms", ""))
        self.described_value_domain = None
        self.value_list = None
        self.links = {
            "parentProduct": self.parent_product.summary["_links"]["self"],
            "self": self._build_self_link(),
        }
        self.validate()

    def _build_self_link(self):
        variable_name = self.transformer.format_name_for_link(self.name, [" ", ",","\n", "\\n", '"', "/", "."])
        datastructure_name = self.transformer.format_name_for_link(self.parent_datastructure_name)
        product_name = self.parent_product.version_prefix + self.parent_product.version
        self_link = {
                "href": f"/mdr/{self.parent_product.model_type}/{product_name}/datastructures/{datastructure_name}/variables/{variable_name}",
                "title": self.label,
                "type": "Analysis Variable"
            }
        return self_link
    
    def set_parent_varset(self, varset):
        self.parent_varset = varset
        self.add_link("parentVarset", varset.links.get("self"))
    
    def add_link(self, key, link):
        self.links[key] = link
    
    def to_json(self):
        json_data = {
            "_links": self.links,
            "name": self.name,
            "label": self.label,
            "simpleDatatype": self.data_type,
            "core": self.core,
            "ordinal": self.ordinal,
            "description": self.description
        }
        
        if self.described_value_domain:
            json_data["describedValueDomain"] = self.described_value_domain
        if self.value_list:
            json_data["valueList"] = self.value_list
        return json_data
    
    def validate(self):
        if not self.label:
            logger.info(f"Variable with name: {self.name} is missing a label. This will cause the title in links to this variable to be empty.")

    def to_string(self):
        string = f"Name: {self.name}, Parent Datastructure: {self.parent_datastructure_name}, Parent Varset: {self.parent_varset_name}"
        return string
