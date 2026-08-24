import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

export interface InfoBlock {
  heading: string;
  body: string;
}

export interface InfoPageData {
  eyebrow: string;
  title: string;
  intro: string;
  blocks: InfoBlock[];
}

@Component({
  selector: 'app-info-page',
  templateUrl: './info-page.component.html',
  styleUrls: ['./info-page.component.scss']
})
export class InfoPageComponent implements OnInit {
  data: InfoPageData | null = null;

  constructor(private route: ActivatedRoute) {}

  ngOnInit(): void {
    this.data = this.route.snapshot.data['info'] as InfoPageData;
  }
}
