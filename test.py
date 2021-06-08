import language
language.initialize('mongodb://localhost:27017/language')

li = ['common.biz', 'common.bc', 'common.cc', 'common.cad', 'common.db', 'common.lc', 'common.dp', 'common.ax', 'common.complete',
              'common.sa', 'common.erd', 'user.refer.title', 'user.refer.refer', 'common.enter_name', 'errors.name', 'common.enter_email',
              'errors.valid_email', 'common.submit', 'common.nutrition_guide', 'dashboard.schedule', 'dashboard.save_factors',
              'dashboard.factor_boxes.*', 'common.learn_more', 'dashboard.take_quiz', 'dashboard.check_risk', 'dashboard.not_complete',
              'dashboard.quiz_learn_more', 'dashboard.risk_categories.diagnosed', 'dashboard.results', 'common.sign_up', 'common.cancers',
              'common.mental_conditions', 'common.general_health', 'common.chronic_conditions', 'common.external_link', 'common.resume',
              'dashboard.finish_quiz', 'dashboard.edit_responses', 'dashboard.responses.*', 'common.apply', 'common.reset_default',
              'common.yes', 'common.no', 'dashboard.reset_answers_msg', 'dashboard.update_answers_msg', 'dashboard.edit_response',
              'dashboard.unreg_learn', 'report_messages.buttons.learn', 'common.nut']

language.get_texts_from_key_list(li)
