import { Component, EventEmitter, Input, Output } from '@angular/core';

@Component({
  selector: 'app-vote-control',
  templateUrl: './vote-control.component.html',
  styleUrls: ['./vote-control.component.scss']
})
export class VoteControlComponent {
  @Input() score = 0;
  @Input() userVote: 1 | -1 | null = null;
  @Input() canVote = true;
  @Input() size: 'md' | 'sm' = 'md';
  @Output() vote = new EventEmitter<1 | -1>();

  onVote(value: 1 | -1): void {
    if (!this.canVote) return;
    this.vote.emit(value);
  }
}
