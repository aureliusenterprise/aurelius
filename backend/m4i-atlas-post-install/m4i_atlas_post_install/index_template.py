publish_state_template = {
    "mappings": {
        "dynamic_templates": [],
        "properties": {
            "attributes": {
                "properties": {
                    "attributes": {
                        "properties": {
                            "guid": {
                                "type": "text",
                                "fields": {
                                    "keyword": {"type": "keyword", "ignore_above": 256}
                                },
                            },
                            "typeName": {
                                "type": "text",
                                "fields": {
                                    "keyword": {"type": "keyword", "ignore_above": 256}
                                },
                            },
                            "uniqueAttributes": {
                                "properties": {
                                    "qualifiedName": {
                                        "type": "text",
                                        "fields": {
                                            "keyword": {
                                                "type": "keyword",
                                                "ignore_above": 256,
                                            }
                                        },
                                    }
                                }
                            },
                        }
                    },
                    "dataDomain": {
                        "properties": {
                            "guid": {
                                "type": "text",
                                "fields": {
                                    "keyword": {"type": "keyword", "ignore_above": 256}
                                },
                            },
                            "typeName": {
                                "type": "text",
                                "fields": {
                                    "keyword": {"type": "keyword", "ignore_above": 256}
                                },
                            },
                            "uniqueAttributes": {
                                "properties": {
                                    "qualifiedName": {
                                        "type": "text",
                                        "fields": {
                                            "keyword": {
                                                "type": "keyword",
                                                "ignore_above": 256,
                                            }
                                        },
                                    }
                                }
                            },
                        }
                    },
                    "dataEntity": {
                        "properties": {
                            "guid": {
                                "type": "text",
                                "fields": {
                                    "keyword": {"type": "keyword", "ignore_above": 256}
                                },
                            },
                            "typeName": {
                                "type": "text",
                                "fields": {
                                    "keyword": {"type": "keyword", "ignore_above": 256}
                                },
                            },
                            "uniqueAttributes": {
                                "properties": {
                                    "qualifiedName": {
                                        "type": "text",
                                        "fields": {
                                            "keyword": {
                                                "type": "keyword",
                                                "ignore_above": 256,
                                            }
                                        },
                                    }
                                }
                            },
                        }
                    },
                    "definition": {
                        "type": "text",
                        "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
                    },
                    "name": {
                        "type": "text",
                        "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
                    },
                    "qualifiedName": {
                        "type": "text",
                        "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
                    },
                    "unmappedAttributes": {"type": "object"},
                }
            },
            "createTime": {"type": "long", "ignore_malformed": False, "coerce": True},
            "createdBy": {
                "type": "text",
                "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
            },
            "displayText": {
                "type": "text",
                "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
            },
            "guid": {
                "type": "text",
                "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
            },
            "isIncomplete": {"type": "boolean"},
            "relationshipAttributes": {
                "properties": {
                    "attributes": {
                        "properties": {
                            "guid": {
                                "type": "text",
                                "fields": {
                                    "keyword": {"type": "keyword", "ignore_above": 256}
                                },
                            },
                            "typeName": {
                                "type": "text",
                                "fields": {
                                    "keyword": {"type": "keyword", "ignore_above": 256}
                                },
                            },
                            "uniqueAttributes": {"type": "object"},
                        }
                    },
                    "dataDomain": {
                        "properties": {
                            "guid": {
                                "type": "text",
                                "fields": {
                                    "keyword": {"type": "keyword", "ignore_above": 256}
                                },
                            },
                            "typeName": {
                                "type": "text",
                                "fields": {
                                    "keyword": {"type": "keyword", "ignore_above": 256}
                                },
                            },
                            "uniqueAttributes": {"type": "object"},
                        }
                    },
                    "dataEntity": {
                        "properties": {
                            "guid": {
                                "type": "text",
                                "fields": {
                                    "keyword": {"type": "keyword", "ignore_above": 256}
                                },
                            },
                            "typeName": {
                                "type": "text",
                                "fields": {
                                    "keyword": {"type": "keyword", "ignore_above": 256}
                                },
                            },
                            "uniqueAttributes": {"type": "object"},
                        }
                    },
                }
            },
            "status": {
                "type": "text",
                "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
            },
            "typeName": {
                "type": "text",
                "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
            },
            "updateTime": {"type": "long", "ignore_malformed": False, "coerce": True},
            "updatedBy": {
                "type": "text",
                "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
            },
            "version": {"type": "long"},
        },
    }
}
