from typing import Optional, List, Dict
import os
import time
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, IntPrompt
from rich.table import Table

from .models import Story, StoryNode, Choice, StoryCreationParams
from .storage import create_story, get_story, add_story_node, save_choice, get_all_stories
from .ai_service import AIService

class StoryGame:
    """Main game class for the terminal-based interactive story experience."""
    
    def __init__(self):
        self.console = Console()
        self.current_story: Optional[Story] = None
        self.current_node: Optional[StoryNode] = None
    
    def start(self):
        """Start the game."""
        self._clear_screen()
        self._print_title()
        
        while True:
            self._clear_screen()
            self._print_title()
            
            self.console.print("\n[bold]Welcome to StoryTeller![/bold]")
            self.console.print("An AI-powered interactive fiction experience.\n")
            
            menu_options = [
                "Start a new story",
                "Continue a saved story",
                "Exit"
            ]
            
            for i, option in enumerate(menu_options, 1):
                self.console.print(f"{i}. {option}")
            
            choice = IntPrompt.ask("\nSelect an option", choices=[str(i) for i in range(1, len(menu_options) + 1)])
            
            if choice == 1:
                self._create_new_story()
            elif choice == 2:
                self._load_story()
            else:
                self.console.print("\nThank you for playing StoryTeller!")
                break
    
    def _create_new_story(self):
        """Create a new story."""
        self._clear_screen()
        self.console.print("[bold]Create New Story[/bold]\n")
        
        # Get character name
        character_name = Prompt.ask("Enter your character's name")
        
        # Choose setting
        settings = {
            "1": "cultivation",
            "2": "gamelike",
            "3": "academy",
            "4": "dungeon",
            "5": "apocalypse",
            "6": "fantasy",
            "7": "scifi",
            "8": "modern"
        }
        self.console.print("\n[bold]Choose a setting:[/bold]")
        for key, value in settings.items():
            self.console.print(f"{key}. {value.capitalize()}")
        setting_choice = Prompt.ask("Select a setting", choices=list(settings.keys()), default="1")
        setting = settings[setting_choice]
        
        # Choose character origin
        origins = {
            "1": "reincarnated",
            "2": "weak",
            "3": "hidden",
            "4": "normal",
            "5": "genius",
            "6": "fallen"
        }
        self.console.print("\n[bold]Choose your character's origin:[/bold]")
        for key, value in origins.items():
            self.console.print(f"{key}. {value.capitalize()}")
        origin_choice = Prompt.ask("Select an origin", choices=list(origins.keys()), default="4")
        character_origin = origins[origin_choice]
        
        # Choose power system
        power_systems = {
            "1": "qi",
            "2": "levels",
            "3": "martial",
            "4": "beast",
            "5": "sword",
            "6": "pills",
            "7": "magic"
        }
        self.console.print("\n[bold]Choose a power system:[/bold]")
        for key, value in power_systems.items():
            self.console.print(f"{key}. {value.capitalize()}")
        power_choice = Prompt.ask("Select a power system", choices=list(power_systems.keys()), default="1")
        power_system = power_systems[power_choice]
        
        # Choose tone
        tones = {
            "1": "adventure",
            "2": "comedy",
            "3": "serious",
            "4": "overpowered",
            "5": "underdog",
            "6": "romance"
        }
        self.console.print("\n[bold]Choose the story tone:[/bold]")
        for key, value in tones.items():
            self.console.print(f"{key}. {value.capitalize()}")
        tone_choice = Prompt.ask("Select a tone", choices=list(tones.keys()), default="1")
        tone = tones[tone_choice]
        
        # Create the story creation parameters
        params = StoryCreationParams(
            character_name=character_name,
            setting=setting,
            tone=tone,
            character_origin=character_origin,
            power_system=power_system
        )
        
        # Generate the initial story with AI
        self.console.print("\n[bold]Generating your story...[/bold]")
        
        try:
            # Generate story content  
            story_content, choices = AIService.generate_initial_story(
                character_name=params.character_name,
                character_gender=params.character_gender,
                setting=params.setting,
                tone=params.tone,
                character_origin=params.character_origin,
                language_complexity=params.language_complexity,
                manga_genre="cultivation_progression" if params.setting == "cultivation" else None
            )
            
            # Create the initial node
            initial_node = StoryNode(
                id="initial",
                content=story_content,
                choices=choices,
                parent_node_id=None
            )
            
            # Create the story
            self.current_story = create_story(params, initial_node)
            self.current_node = initial_node
            
            # Continue with the story
            self._continue_story()
            
        except Exception as e:
            self.console.print(f"[bold red]Error creating story:[/bold red] {str(e)}")
            input("\nPress Enter to return to the main menu...")
    
    def _load_story(self):
        """Load a saved story."""
        self._clear_screen()
        self.console.print("[bold]Load Saved Story[/bold]\n")
        
        # Get all stories
        stories = get_all_stories()
        
        if not stories:
            self.console.print("[italic]No saved stories found.[/italic]")
            input("\nPress Enter to return to the main menu...")
            return
        
        # Display stories
        table = Table(title="Your Stories")
        table.add_column("#", justify="right", style="cyan")
        table.add_column("Title", style="green")
        table.add_column("Character", style="yellow")
        table.add_column("Setting", style="blue")
        table.add_column("Last Updated", style="magenta")
        
        for i, story in enumerate(stories, 1):
            # Format last updated timestamp
            last_updated = time.strftime("%Y-%m-%d %H:%M", time.localtime(story.last_updated))
            
            table.add_row(
                str(i),
                story.title,
                story.character_name,
                story.setting.capitalize(),
                last_updated
            )
        
        self.console.print(table)
        
        # Choose a story
        choice = IntPrompt.ask(
            "\nSelect a story number (0 to return)",
            choices=["0"] + [str(i) for i in range(1, len(stories) + 1)]
        )
        
        if choice == 0:
            return
        
        # Load the selected story
        selected_story = stories[choice - 1]
        self.current_story = get_story(selected_story.id)
        
        if not self.current_story:
            self.console.print("[bold red]Error:[/bold red] Failed to load story.")
            input("\nPress Enter to return to the main menu...")
            return
        
        # Get the current node
        self.current_node = self.current_story.nodes.get(self.current_story.current_node_id)
        
        if not self.current_node:
            self.console.print("[bold red]Error:[/bold red] Story data is corrupted.")
            input("\nPress Enter to return to the main menu...")
            return
        
        # Continue with the story
        self._continue_story()
    
    def _continue_story(self):
        """Continue the current story."""
        if not self.current_story or not self.current_node:
            self.console.print("[bold red]Error:[/bold red] No story is loaded.")
            return
        
        while True:
            self._clear_screen()
            
            # Print story header
            self._print_story_header()
            
            # Print the story content
            story_text = Text(self.current_node.content)
            panel = Panel(
                story_text,
                title=self.current_story.title,
                subtitle=f"Node: {self.current_node.id}",
                padding=(1, 2)
            )
            self.console.print(panel)
            
            # Print choices
            self.console.print("\n[bold]What will you do?[/bold]")
            
            for i, choice in enumerate(self.current_node.choices, 1):
                self.console.print(f"{i}. {choice.text}")
            
            self.console.print("0. Save and return to main menu")
            
            # Get user choice
            choice_num = IntPrompt.ask(
                "\nEnter your choice",
                choices=["0"] + [str(i) for i in range(1, len(self.current_node.choices) + 1)]
            )
            
            if choice_num == 0:
                # Return to main menu
                return
            
            # Process the choice
            selected_choice = self.current_node.choices[choice_num - 1]
            self.console.print(f"\nYou chose: {selected_choice.text}")
            
            # Save the choice
            save_choice(self.current_story.id, self.current_node.id, selected_choice.id)
            
            # Generate continuation
            self.console.print("\n[bold]Generating story continuation...[/bold]")
            
            try:
                # Generate story content
                story_content, choices = AIService.continue_story(
                    character_name=self.current_story.character_name,
                    character_gender=self.current_story.character_gender,
                    setting=self.current_story.setting,
                    tone=self.current_story.tone,
                    previous_content=self.current_node.content,
                    selected_choice=selected_choice.text
                )
                
                # Create the new node
                new_node_id = f"node_{int(time.time())}"
                new_node = StoryNode(
                    id=new_node_id,
                    content=story_content,
                    choices=choices,
                    parent_node_id=self.current_node.id,
                    selected_choice_id=selected_choice.id
                )
                
                # Save the new node
                updated_story = add_story_node(self.current_story.id, new_node)
                
                if updated_story:
                    self.current_story = updated_story
                    self.current_node = new_node
                else:
                    raise Exception("Failed to update story")
                
            except Exception as e:
                self.console.print(f"[bold red]Error continuing story:[/bold red] {str(e)}")
                input("\nPress Enter to continue...")
    
    def _print_story_header(self):
        """Print the story header with character info."""
        if not self.current_story:
            return
        
        # Create header table
        table = Table(show_header=False, show_edge=False, box=None, padding=(0, 1))
        table.add_column("Key", style="dim")
        table.add_column("Value", style="bold")
        
        table.add_row("Character", self.current_story.character_name)
        table.add_row("Setting", self.current_story.setting.capitalize())
        
        if self.current_story.cultivation_stage:
            table.add_row("Cultivation", self.current_story.cultivation_stage)
        
        self.console.print(table)
    
    def _print_title(self):
        """Print the game title."""
        title = """
███████╗████████╗ ██████╗ ██████╗ ██╗   ██╗████████╗███████╗██╗     ██╗     ███████╗██████╗ 
██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗╚██╗ ██╔╝╚══██╔══╝██╔════╝██║     ██║     ██╔════╝██╔══██╗
███████╗   ██║   ██║   ██║██████╔╝ ╚████╔╝    ██║   █████╗  ██║     ██║     █████╗  ██████╔╝
╚════██║   ██║   ██║   ██║██╔══██╗  ╚██╔╝     ██║   ██╔══╝  ██║     ██║     ██╔══╝  ██╔══██╗
███████║   ██║   ╚██████╔╝██║  ██║   ██║      ██║   ███████╗███████╗███████╗███████╗██║  ██║
╚══════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝   ╚═╝      ╚═╝   ╚══════╝╚══════╝╚══════╝╚══════╝╚═╝  ╚═╝
                                                                                            
        """
        self.console.print(f"[bold cyan]{title}[/bold cyan]")
        self.console.print("[italic]An AI-powered interactive fiction experience[/italic]", justify="center")
    
    def _clear_screen(self):
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear') 