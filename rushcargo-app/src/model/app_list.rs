use anyhow::Result;
use sqlx::PgPool;
use ratatui::widgets::{ListItem as ListItemRt, ListState};
use super::{
    common::Screen,
    app::App,
};

#[derive(Debug)]
pub enum ListType {
    Title,
    Settings,
}

trait ListItem {
    fn len(&self) -> usize;
}

impl ListItem for Vec<&str> {
    fn len(&self) -> usize {
        Vec::len(self)
    }
}

pub struct ListStates(pub ListState, pub ListState);

pub struct ListActions {
    pub title: Vec<&'static str>,
    pub settings: Vec<&'static str>,
}

pub struct ListData {
    pub state: ListStates,
    pub actions: ListActions,
}

impl std::default::Default for ListData {
    fn default() -> Self {
        ListData {
            state: ListStates(
                ListState::default(),
                ListState::default(),
            ),
            actions: ListActions {
                title: vec![
                    "Login",
                    "Settings",
                    "Quit",
                ],
                settings: vec![
                    "Display animation: ",
                ]
            }
        }
    }
}

impl App {
    pub fn next_list_item(&mut self, list_type: ListType) {
        let (list_state, items): (_, &dyn ListItem) = match list_type {
            ListType::Title => (&mut self.list.state.0, &self.list.actions.title),
            ListType::Settings => (&mut self.list.state.0, &self.list.actions.settings),
        };

        let i = match list_state.selected() {
            Some(i) => {
                if i >= items.len() - 1 {
                    0
                } else {
                    i + 1
                }
            }
            None => 0,
        };
        list_state.select(Some(i));
    }
    
    pub fn prev_list_item(&mut self, list_type: ListType) {
        let (list_state, items): (_, &dyn ListItem) = match list_type {
            ListType::Title => (&mut self.list.state.0, &self.list.actions.title),
            ListType::Settings => (&mut self.list.state.0, &self.list.actions.settings),
        };

        let i = match list_state.selected() {
            Some(i) => {
                if i == 0 {
                    items.len() - 1
                } else {
                    i - 1
                }
            }
            None => 0,
        };
        list_state.select(Some(i));
    }
}