from dash import html, dcc

BUTTONS = [
    ("File Upload",  'file_upload'),
    ("Task Configurations", 'task_config'),
    ("Search Space", 'search_space'),
    ("Review", 'review')
]
# <ul id="progressbar">
#                         <li class="active" id="account"><strong>Account</strong></li>
#                         <li id="personal"><strong>Personal</strong></li>
#                         <li id="payment"><strong>Image</strong></li>
#                         <li id="confirm"><strong>Finish</strong></li>
#                     </ul>

def submission():
    return html.Div(
        className="submission_form_container", 
        id="submission_form_container",
        children=[
            html.Div(
                className="submission_form_title_progress_container", 
                children=[
                    html.Div(
                        className="submission_form_title_container", 
                        children=[
                            html.H1("Task Submission"), 
                            html.P("Follow these steps to submit your task.")
                        ]
                    ),
                    html.Div(
                        className="submission_form_progress_bar_container", 
                        children=[
                            html.Div(
                                className="submission_form_progress_bar", 
                                children=[
                                    html.Ul(
                                        id="progressbar", 
                                        children=[
                                            html.Li(
                                                className='active' if i<2 else "",
                                                id=BUTTONS[i][1],
                                                children=[html.P(BUTTONS[i][0])]
                                            ) for i in range(len(BUTTONS))
                                        ]
                                    )
                                ]
                            )
                        ]
                    )
                ]
            ),
            html.Div(
                id="submission_form_body_container", 
                className="submission_form_body_container",
                children=["submission"]
            )
        ]
    )


# <div class="form__container">
#     <div class="title__container">
#         <h1>Example UI container</h1>
#         <p>Follow the 4 simple steps to complete your mapping</p>
#     </div>
#     <div class="body__container">
#         <div class="left__container">
#             <div class="side__titles">
#                 <div class="title__name">
#                     <h3>Your name</h3>
#                     <p>Enter & press next</p>
#                 </div>
#                 <div class="title__name">
#                     <h3>Desctibes</h3>
#                     <p>select & press next</p>
#                 </div>
#                 <div class="title__name">
#                     <h3>Services</h3>
#                     <p>select & press next</p>
#                 </div>
#                 <div class="title__name">
#                     <h3>Budget</h3>
#                     <p>Select & press next</p>
#                 </div>
#                 <div class="title__name">
#                     <h3>Complete</h3>
#                     <p>Finaly press submit</p>
#                 </div>
#             </div>
#             <div class="progress__bar__container">
#                 <ul>
#                     <li class="active" id="icon1">
#                         <ion-icon name="person-outline"></ion-icon>
#                     </li>
#                     <li id="icon2">
#                         <ion-icon name="book-outline"></ion-icon>
#                     </li>
#                     <li id="icon3">
#                         <ion-icon name="layers-outline"></ion-icon>
#                     </li>
#                     <li id="icon4">
#                         <ion-icon name="pricetag-outline"></ion-icon>
#                     </li>
#                     <li id="icon5">
#                         <ion-icon name="mail-outline"></ion-icon>
#                     </li>
#                 </ul>
#             </div>
#         </div>
#         <div class="right__container">
#             <fieldset id="form1">
#                 <div class="sub__title__container ">
#                     <p>Step 1/5</p>
#                     <h2>Let's start with your name</h2>
#                     <p>Please fill the details below so that we can we can get in contacat with you about our product</p>
#                 </div>
#                 <div class="input__container"> <label for="name">Enter your name</label> <input type="text"> <a class="nxt__btn" onclick="nextForm();"> Next</a> </div>
#             </fieldset>
#             <fieldset class="active__form" id="form2">
#                 <div class="sub__title__container">
#                     <p>Step 2/5</p>
#                     <h2>What best describes you ?</h2>
#                     <p>Please let us know what type of business best describes you as entreprenuer or businessman.</p>
#                 </div>
#                 <div class="input__container">
#                     <div class="selection newB">
#                         <div class="imoji">
#                             <ion-icon name="happy"></ion-icon>
#                         </div>
#                         <div class="descriptionTitle">
#                             <h3>New Business</h3>
#                             <p>Started trading in last 12 months</p>
#                         </div>
#                     </div>
#                     <div class="selection exitB">
#                         <div class="imoji">
#                             <ion-icon name="business"></ion-icon>
#                         </div>
#                         <div class="descriptionTitle">
#                             <h3>Existing Business</h3>
#                             <p>Have been operating beyond 12 months</p>
#                         </div>
#                     </div>
#                     <div class="buttons"> <a class="prev__btn" onclick="prevForm();">Back</a> <a class="nxt__btn" onclick="nextForm();">Next</a> </div>
#                 </div>
#             </fieldset>
#             <fieldset class="active__form" id="form3">
#                 <div class="sub__title__container">
#                     <p>Step 3/5</p>
#                     <h2>What service are looking for ?</h2>
#                     <p>Please let us know what type of business best describes you as entreprenuer or businessman.</p>
#                 </div>
#                 <div class="input__container">
#                     <div class="selection newB">
#                         <div class="imoji">
#                             <ion-icon name="desktop"></ion-icon>
#                         </div>
#                         <div class="descriptionTitle">
#                             <h3>Website Development</h3>
#                             <p>Development of online websites</p>
#                         </div>
#                     </div>
#                     <div class="selection exitB">
#                         <div class="imoji">
#                             <ion-icon name="phone-portrait"></ion-icon>
#                         </div>
#                         <div class="descriptionTitle">
#                             <h3>Development of Mobile App</h3>
#                             <p>Development of android and IOS mobile app</p>
#                         </div>
#                     </div>
#                     <div class="buttons"> <a class="prev__btn" onclick="prevForm();">Back</a> <a class="nxt__btn" onclick="nextForm();">Next</a> </div>
#                 </div>
#             </fieldset>
#             <fieldset class="active__form" id="form4">
#                 <div class="sub__title__container">
#                     <p>Step 4/5</p>
#                     <h2>Please select your budget</h2>
#                     <p>Please let us know budget for your project so yes are great that we can give the right quote thanks</p>
#                 </div>
#                 <div class="input__container"> <input type="range" min="10000" max="500000" value="250000" class="slider">
#                     <div class="output__value"> </div>
#                     <div class="buttons"> <a class="prev__btn" onclick="prevForm();">Back</a> <a class="nxt__btn" onclick="nextForm();">Next</a> </div>
#                 </div>
#             </fieldset>
#             <fieldset class="active__form" id="form5">
#                 <div class="sub__title__container">
#                     <p>Step 5/5</p>
#                     <h2>Complete Submission</h2>
#                     <p>Thanks for completing the form and for your time.Plss enter your email below and submit the form</p>
#                 </div>
#                 <div class="input__container"> <label for="Email">Enter your email</label> <input type="text">
#                     <div class="buttons"> <a class="prev__btn" onclick="prevForm();">Back</a> <a class="nxt__btn" id="submitBtn" onclick="nextForm();">Next</a> </div>
#                 </div>
#             </fieldset>
#         </div>
#     </div>
# </div>
# <script type="module" src="https://unpkg.com/ionicons@5.5.2/dist/ionicons/ionicons.esm.js"></script>
# <script nomodule src="https://unpkg.com/ionicons@5.5.2/dist/ionicons/ionicons.js"></script>