import os
import numpy as np
from random import shuffle
from collections import deque

from AI.CNN_player import CNN_Player 
from arena import Arena

from AI.utils.Monte_Carlo import MonteCarloTreeSearch
from engine.environment.aienvironment import ai_environment
from pickle import Pickler

class Trainer:

    def __init__(self, model, train_args, nnet_args):
        self.model = model
        self.comp_model = self.model.__class__(nnet_args)    # competitor network for self play
        self.args = train_args
        self.train_examples_history = []
        self.mcts = MonteCarloTreeSearch(self.model, self.args)

    def execute_episode(self):

        train_examples = []
        current_player = 1
        state = ai_environment.get_init_board()

        while True:
            canonical_board = ai_environment.get_canonical_form(state, current_player)

            self.mcts = MonteCarloTreeSearch(self.model, self.args)
            root = self.mcts.run(self.model, canonical_board, state, to_play=1)

            action_probs = [0 for _ in range(ai_environment.get_action_size())]
            for k, v in root.children.items():
                action_probs[k] = v.visits_count

            action_probs = action_probs / np.sum(action_probs)
            train_examples.append((canonical_board, current_player, action_probs))

            action = root.select_best_child()
            state, current_player = ai_environment.get_next_state(state, current_player, action[0])
            reward = ai_environment.get_game_ended(state, current_player)

            if reward != 0:
                replay_buffer = []
                for hist_state, hist_current_player, hist_action_probs in train_examples:
                    # [Board, currentPlayer, actionProbabilities, Reward]
                    replay_buffer.append((hist_state, hist_action_probs, reward * ((-1) ** (hist_current_player != current_player))))

                return replay_buffer

    def learn(self):
        
        for i in range(0, self.args.numIters):
            print('---------Iteration ' + str(i+1) + '------------')

            if i > 0:
                iteration_train_examples = deque([])

                for eps in range(self.args.numEps):
                    self.mcts = MonteCarloTreeSearch(self.model, self.args)
                    iteration_train_examples.append(self.execute_episode())

                
                self.train_examples_history.append(iteration_train_examples)

        if len(self.train_examples_history) > self.args.numItersForTrainExamplesHistory:
            self.train_examples_history.pop(0)

        self.save_checkpoint(self.args.checkpoint, "checkpoint_examples")

        # shuffling the training exmaples
        train_examples = []
        for example in self.train_examples_history:
            train_examples.extend(example)
        shuffle(train_examples)

        self.model.save_checkpoint(folder = self.args.checkpoint)
        self.comp_model.load_checkpoint(folder = self.args.checkpoint)

        comp_cnn_player = CNN_Player(self.comp_model, self.args)
        self.model.train(train_examples)
        cnn_player = CNN_Player(self.model, self.args)

        print("------------Initiating Self Play--------------")
        arena = Arena(cnn_player, comp_cnn_player)
        wins, comp_wins, draws = arena.playGames(self.args.arenaCompare)

        print("W:L:D  -  %d:%d:%d".format(wins, comp_wins, draws))

        if comp_wins * self.args.updateThreshold > wins or comp_wins + wins == 0:
            print("SELECTING OLD MODEL")
            self.model.load_checkpoint(folder=self.args.checkpoint, filename='temp.pth.tar')
        else:
            print("SELECTING NEW MODEL")
            iter_filename = 'checkpoint_' + str(i) + '.pth.tar'
            self.model.save_checkpoint(folder=self.args.checkpoint, filename= iter_filename)
            self.model.save_checkpoint(folder=self.args.checkpoint, filename='best.pth.tar')

            

    def save_checkpoint(self, folder, filename):
        if not os.path.exists(folder):
            os.mkdir(folder)

        filepath = os.path.join(folder, filename)

        with open(filepath, "wb+") as f:
            Pickler(f).dump(self.train_examples_history)

