use tauri_plugin_shell::ShellExt;
use tauri_plugin_shell::process::CommandEvent;
use tauri::{Emitter, Manager};
use std::sync::Mutex;
use serde::{Serialize, Deserialize};

#[derive(Clone, Serialize, Deserialize)]
pub struct SidecarConfig {
    pub port: String,
    pub token: String,
}

struct SidecarState {
    config: Mutex<Option<SidecarConfig>>,
}

#[tauri::command]
fn get_sidecar_config(state: tauri::State<'_, SidecarState>) -> Option<SidecarConfig> {
    state.config.lock().unwrap().clone()
}

#[tauri::command]
fn get_sidecar_port(state: tauri::State<'_, SidecarState>) -> Option<String> {
    state.config.lock().unwrap().as_ref().map(|c| c.port.clone())
}

#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .manage(SidecarState {
            config: Mutex::new(None),
        })
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_shell::init())
        .invoke_handler(tauri::generate_handler![greet, get_sidecar_port, get_sidecar_config])
        .setup(|app| {
            let handle = app.handle().clone();
            let sidecar = app.shell().sidecar("sidecar").unwrap();
            let (mut rx, _child) = sidecar.spawn().expect("Failed to spawn sidecar");

            tauri::async_runtime::spawn(async move {
                let mut current_port = None;
                let mut current_token = None;

                while let Some(event) = rx.recv().await {
                    match event {
                        CommandEvent::Stdout(line) => {
                            let out = String::from_utf8_lossy(&line);
                            let out_str = out.to_string(); // Keep for logging if needed
                            println!("[Sidecar]: {}", out_str); // Re-enabled for debugging

                            for line in out_str.lines() {
                                if line.contains("PORT:") {
                                    if let Some(port_part) = line.split("PORT:").last() {
                                        let port = port_part.trim().to_string();
                                        if !port.is_empty() {
                                            println!("Sidecar Port Detected: {}", port);
                                            current_port = Some(port);
                                        }
                                    }
                                }
                                if line.contains("TOKEN:") {
                                    if let Some(token_part) = line.split("TOKEN:").last() {
                                        let token = token_part.trim().to_string();
                                        if !token.is_empty() {
                                            println!("Sidecar Token Detected");
                                            current_token = Some(token);
                                        }
                                    }
                                }
                            }

                            // If both are found, update state and emit
                            if let (Some(port), Some(token)) = (&current_port, &current_token) {
                                let config = SidecarConfig {
                                    port: port.clone(),
                                    token: token.clone(),
                                };
                                
                                {
                                    let state = handle.state::<SidecarState>();
                                    let mut state_lock = state.config.lock().unwrap();
                                    
                                    // Check if config is new or changed (though port usually stays same)
                                    let is_new = state_lock.is_none();
                                    if is_new {
                                        *state_lock = Some(config.clone());
                                        println!("Sidecar fully configured. Emitting sidecar-ready.");
                                        handle.emit("sidecar-ready", config).unwrap();
                                    }
                                }
                            }
                        }
                        CommandEvent::Stderr(line) => {
                            eprintln!("[PY ERR]: {}", String::from_utf8_lossy(&line));
                        }
                        CommandEvent::Terminated(status) => {
                            println!("Sidecar terminated with status: {:?}", status);
                            handle.emit("sidecar-error", format!("Sidecar process terminated with code {:?}", status.code)).unwrap();
                        }
                        _ => {}
                    }
                }
            });
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
