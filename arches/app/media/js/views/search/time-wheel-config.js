define([], function() {
    return {
        "name": "root",
        "children": [{
                "name": "Historic",
                "children": [{
                        "name": "21st Century",
                        "size": 75,
                        "hits": 2001
                    },
                    {
                        "name": "20th Century",
                        "children": [{
                                "name": "Late 20th Century",
                                "size": 230,
                                "hits": 1965
                            },
                            {
                                "name": "Middle 20th Century",
                                "size": 190,
                                "hits": 1950
                            },
                            {
                                "name": "WWII",
                                "size": 207,
                                "hits": 1939
                            },
                            {
                                "name": "Early 20th Century",
                                "children": [{
                                        "name": "WWI",
                                        "size": 377,
                                        "hits": 1914
                                    },
                                    {
                                        "name": "Post WWI",
                                        "size": 632,
                                        "hits": 1918
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "name": "Enlightenment",
                        "children": [{
                                "name": "1900s",
                                "size": 1003,
                                "hits": 1900
                            },
                            {
                                "name": "1800s",
                                "size": 2108,
                                "hits": 1800
                            },
                            {
                                "name": "1700s",
                                "size": 1533,
                                "hits": 1700
                            },
                            {
                                "name": "1600s",
                                "size": 2312,
                                "hits": 1600
                            }
                        ]
                    },
                    {
                        "name": "Post Midieval",
                        "children": [{
                                "name": "Victorian",
                                "size": 3861,
                                "hits": 1400
                            },
                            {
                                "name": "Hannoverian",
                                "children": [{
                                        "name": "George I",
                                        "size": 2877,
                                        "hits": 1380
                                    },
                                    {
                                        "name": "George Ib",
                                        "size": 1187,
                                        "hits": 1380
                                    }
                                ]
                            },
                            {
                                "name": "Stuart",
                                "children": [{
                                    "name": "Jacobean",
                                    "size": 961,
                                    "hits": 1340
                                }]
                            },
                            {
                                "name": "Tudor",
                                "children": [{
                                    "name": "Elizabethian",
                                    "size": 1900,
                                    "hits": 1300
                                }]
                            }
                        ]
                    },
                    {
                        "name": "Midieval",
                        "children": [{
                                "name": "Late Midieval",
                                "size": 4134,
                                "hits": 1100
                            },
                            {
                                "name": "Early Midieval",
                                "size": 7399,
                                "hits": 900
                            }
                        ]
                    },
                    {
                        "name": "Roman",
                        "size": 18012,
                        "hits": 43
                    }
                ]
            },
            {
                "name": "Prehistoric",
                "children": [{
                        "name": "Late Prehistoric",
                        "children": [{
                                "name": "Iron Age",
                                "children": [{
                                        "name": "Late Iron",
                                        "size": 2977,
                                        "hits": 0
                                    },
                                    {
                                        "name": "Middle Iron",
                                        "size": 3866,
                                        "hits": -400
                                    },
                                    {
                                        "name": "Early Iron",
                                        "size": 5219,
                                        "hits": -800
                                    }
                                ]
                            },
                            {
                                "name": "Bronze Age",
                                "children": [{
                                        "name": "Late Bronze",
                                        "size": 1883,
                                        "hits": -1000
                                    },
                                    {
                                        "name": "Middle Bronze",
                                        "size": 2016,
                                        "hits": -1200
                                    },
                                    {
                                        "name": "Early Bronze",
                                        "size": 300,
                                        "hits": -1800
                                    }
                                ]
                            },
                            {
                                "name": "Neolithic",
                                "children": [{
                                        "name": "Late Neolithic",
                                        "size": 2196,
                                        "hits": -2000
                                    },
                                    {
                                        "name": "Middle Neolithic",
                                        "size": 2445,
                                        "hits": -3000
                                    },
                                    {
                                        "name": "Early Neolithic",
                                        "size": 988,
                                        "hits": -4500
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "name": "Early Prehistoric",
                        "children": [{
                                "name": "Mesolithic",
                                "children": [{
                                        "name": "Late Mesolithic",
                                        "size": 875,
                                        "hits": -6000
                                    },
                                    {
                                        "name": "Early Mesolithic",
                                        "size": 775,
                                        "hits": -8000
                                    }
                                ]
                            },
                            {
                                "name": "Paleolithic",
                                "children": [{
                                        "name": "Upper Paleolithic",
                                        "size": 3997,
                                        "hits": -10000
                                    },
                                    {
                                        "name": "Middle Paleolithic",
                                        "size": 1009,
                                        "hits": -13000
                                    },
                                    {
                                        "name": "Lower Paleolithic",
                                        "size": 8877,
                                        "hits": -15000
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    };
});
