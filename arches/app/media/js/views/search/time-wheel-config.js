define([], function() {
    return {
        "name": "root",
        "children": [{
                "name": "Historic",
                "children": [{
                        "name": "21st Century",
                        "size": 75,
                        "start": 2001,
                        "end": 2100
                    },
                    {
                        "name": "20th Century",
                        "start": 1901,
                        "end": 2000,
                        "children": [{
                                "name": "Late 20th Century",
                                "size": 230,
                                "start": 1965,
                                "end": 1999
                            },
                            {
                                "name": "Middle 20th Century",
                                "size": 190,
                                "start": 1945,
                                "end": 1965
                            },
                            {
                                "name": "WWII",
                                "size": 207,
                                "start": 1939,
                                "end": 1945
                            },
                            {
                                "name": "Early 20th Century",
                                "start": 1900,
                                "end": 1939,
                                "children": [{
                                        "name": "WWI",
                                        "size": 377,
                                        "start": 1914,
                                        "end": 1918
                                    },
                                    {
                                        "name": "Post WWI",
                                        "size": 632,
                                        "start": 1918,
                                        "end": 1939
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "name": "Enlightenment",
                        "start": 1600,
                        "end": 2000,
                        "children": [{
                                "name": "1900s",
                                "size": 1003,
                                "start": 1900,
                                "end": 2000
                            },
                            {
                                "name": "1800s",
                                "size": 2108,
                                "start": 1800,
                                "end": 1900
                            },
                            {
                                "name": "1700s",
                                "size": 1533,
                                "start": 1700,
                                "end": 1800
                            },
                            {
                                "name": "1600s",
                                "size": 2312,
                                "start": 1600,
                                "end": 1700
                            }
                        ]
                    },
                    {
                        "name": "Post Midieval",
                        "start": 1300,
                        "end": 1600,
                        "children": [{
                                "name": "Victorian",
                                "size": 3861,
                                "start": 1400,
                                "end": 1500
                            },
                            {
                                "name": "Hannoverian",
                                "start": 1380,
                                "end": 1380,
                                "children": [{
                                        "name": "George I",
                                        "size": 2877,
                                        "start": 1380,
                                        "end": 1380
                                    },
                                    {
                                        "name": "George Ib",
                                        "size": 1187,
                                        "start": 1380,
                                        "end": 1380
                                    }
                                ]
                            },
                            {
                                "name": "Stuart",
                                "start": 1340,
                                "end": 1380,
                                "children": [{
                                    "name": "Jacobean",
                                    "size": 961,
                                    "start": 1340,
                                    "end": 1380
                                }]
                            },
                            {
                                "name": "Tudor",
                                "start": 1300,
                                "end": 1340,
                                "children": [{
                                    "name": "Elizabethian",
                                    "size": 1900,
                                    "start": 1300,
                                    "end": 1340
                                }]
                            }
                        ]
                    },
                    {
                        "name": "Midieval",
                        "start": 900,
                        "end": 1300,
                        "children": [{
                                "name": "Late Midieval",
                                "size": 4134,
                                "start": 1100,
                                "end": 1300
                            },
                            {
                                "name": "Early Midieval",
                                "size": 7399,
                                "start": 900,
                                "end": 1100
                            }
                        ]
                    },
                    {
                        "name": "Roman",
                        "size": 18012,
                        "start": 43,
                        "end": 900
                    }
                ]
            },
            {
                "name": "Prehistoric",
                "start": -15000,
                "end": 43,
                "children": [{
                        "name": "Late Prehistoric",
                        "children": [{
                                "name": "Iron Age",
                                "start": -800,
                                "end": 43,
                                "children": [{
                                        "name": "Late Iron",
                                        "size": 2977,
                                        "start": 0,
                                        "end": 43
                                    },
                                    {
                                        "name": "Middle Iron",
                                        "size": 3866,
                                        "start": -400,
                                        "end": 0
                                    },
                                    {
                                        "name": "Early Iron",
                                        "size": 5219,
                                        "start": -800,
                                        "end": -400
                                    }
                                ]
                            },
                            {
                                "name": "Bronze Age",
                                "start": -1800,
                                "end": -800,
                                "children": [{
                                        "name": "Late Bronze",
                                        "size": 1883,
                                        "start": -1000,
                                        "end": -800
                                    },
                                    {
                                        "name": "Middle Bronze",
                                        "size": 2016,
                                        "start": -1200,
                                        "end": -1000
                                    },
                                    {
                                        "name": "Early Bronze",
                                        "size": 300,
                                        "start": -1800,
                                        "end": -1200
                                    }
                                ]
                            },
                            {
                                "name": "Neolithic",
                                "start": -4500,
                                "end": -1800,
                                "children": [{
                                        "name": "Late Neolithic",
                                        "size": 2196,
                                        "start": -2000,
                                        "end": -1800
                                    },
                                    {
                                        "name": "Middle Neolithic",
                                        "size": 2445,
                                        "start": -3000,
                                        "end": -2000
                                    },
                                    {
                                        "name": "Early Neolithic",
                                        "size": 988,
                                        "start": -4500,
                                        "end": -3000
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "name": "Early Prehistoric",
                        "start": -15000,
                        "end": -4500,
                        "children": [{
                                "name": "Mesolithic",
                                "children": [{
                                        "name": "Late Mesolithic",
                                        "size": 875,
                                        "start": -6000,
                                        "end": -4500
                                    },
                                    {
                                        "name": "Early Mesolithic",
                                        "size": 775,
                                        "start": -8000,
                                        "end": -6000
                                    }
                                ]
                            },
                            {
                                "name": "Paleolithic",
                                "start": -15000,
                                "end": -8000,
                                "children": [{
                                        "name": "Upper Paleolithic",
                                        "size": 3997,
                                        "start": -10000,
                                        "end": -8000
                                    },
                                    {
                                        "name": "Middle Paleolithic",
                                        "size": 1009,
                                        "start": -13000,
                                        "end": -10000
                                    },
                                    {
                                        "name": "Lower Paleolithic",
                                        "size": 8877,
                                        "start": -15000,
                                        "end": -13000
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
